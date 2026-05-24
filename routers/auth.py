# ============================================
# 认证路由模块
# 功能：用户登录、注册、登出、JWT令牌管理、密码加密验证
# 路由前缀：/auth
# ============================================

# 导入time delta和datetime类，用于处理令牌过期时间计算
from datetime import timedelta, datetime
# 导入os模块，用于从环境变量中读取JWT密钥配置
import os

# 导入FastAPI核心组件：APIRouter（路由）、Depends（依赖注入）、HTTPException（异常）、Form（表单数据）
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
# 导入HTTP状态码常量
from starlette import status
# 导入RedirectResponse用于请求重定向
from starlette.responses import RedirectResponse
# 导入Pydantic的BaseModel，用于定义数据验证模型
from pydantic import BaseModel
# 导入类型注解工具：Optional表示可选类型
from typing import Optional
# 导入SQLAlchemy的Session类，用于数据库会话操作
from sqlalchemy.orm import Session

# 导入数据模型模块（Users、Todos）
import models
# 导入数据库会话工厂和引擎实例
from database import SessionLocal, engine
# 导入用户数据模型类
from models import Users
# 导入passlib的CryptContext，用于密码的bcrypt加密和验证
from passlib.context import CryptContext
# 导入OAuth2表单和Bearer令牌认证工具
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
# 导入jose库的jwt模块，用于JSON Web Token的编码和解码
from jose import jwt, JWTError
# 导入Jinja2模板引擎，用于渲染HTML模板
from fastapi.templating import Jinja2Templates
# 导入HTMLResponse响应类
from fastapi.responses import HTMLResponse

# ============================================
# 路由器配置
# ============================================
# 创建API路由器实例，所有路由都会自动添加 /auth 前缀
router = APIRouter(
    prefix="/auth",  # 路由URL前缀
    tags=["auth"],   # API文档分组标签
    responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}}  # 默认404响应
)

# ============================================
# JWT配置
# ============================================
# 从环境变量中获取JWT签名密钥，如果未设置则使用默认值（生产环境务必修改）
SECRET_KEY = os.getenv("SECRET_KEY", "197b2c37")
# JWT签名算法：HS256（HMAC-SHA256对称加密算法）
ALGORITHM = "HS256"

# ============================================
# 模板引擎配置
# ============================================
# 初始化Jinja2模板引擎，指定模板文件存放目录为项目根目录下的templates文件夹
templates = Jinja2Templates(directory="templates")

# ============================================
# 密码加密配置
# ============================================
# 创建bcrypt密码加密上下文
# schemes=["bcrypt"]：使用bcrypt加密方案
# deprecated="auto"：自动处理已弃用的加密版本
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 确保数据库表结构已创建（防御性编程，确保表存在）
models.Base.metadata.create_all(bind=engine)

# 创建OAuth2密码Bearer令牌认证实例
# tokenUrl：指定获取令牌的API路径（完整路径为 /auth/token）
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")


# ============================================
# Pydantic数据模型
# ============================================

# 令牌响应模型：定义API返回的JWT令牌数据结构
class Token(BaseModel):
    access_token: str  # JWT访问令牌字符串
    token_type: str    # 令牌类型，通常为"bearer"


# 登录表单辅助类：封装从HTML表单中提取用户名和密码的逻辑
class LoginForm:
    def __init__(self, request: Request):
        # 保存HTTP请求对象引用
        self.request = request
        # 初始化用户名和密码为None
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        """从请求中异步解析表单数据，提取用户名和密码"""
        form = await self.request.form()  # 异步获取表单数据（必须使用await）
        self.username = form.get("username")  # 获取用户名字段
        self.password = form.get("password")  # 获取密码字段


# ============================================
# 数据库会话依赖
# ============================================

def get_db():
    """
    数据库会话依赖注入生成器
    每次请求创建一个新的数据库会话，请求结束后自动关闭
    """
    db = SessionLocal()  # 创建新的数据库会话实例
    try:
        yield db  # 产出会话给路由处理函数使用
    finally:
        db.close()  # 无论请求成功或失败，最终都要关闭会话释放连接


# ============================================
# 密码工具函数
# ============================================

def get_password_hash(password: str) -> str:
    """
    对明文密码进行bcrypt哈希加密
    参数：password - 明文密码
    返回：加密后的哈希字符串
    """
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与哈希密码匹配
    参数：plain_password - 用户输入的明文密码
          hashed_password - 数据库中存储的哈希密码
    返回：匹配成功返回True，否则返回False
    """
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db: Session):
    """
    验证用户身份：根据用户名查找用户，然后验证密码
    参数：username - 登录用户名
          password - 明文密码
          db - 数据库会话
    返回：验证成功返回用户对象，失败返回False
    """
    # 在数据库中查找匹配用户名的用户记录
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False  # 用户不存在
    if not verify_password(password, user.hashed_password):
        return False  # 密码不匹配
    return user  # 验证通过，返回用户对象


# ============================================
# JWT令牌工具函数
# ============================================

def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """
    生成JWT访问令牌
    参数：username - 用户名（存入令牌的sub字段）
          user_id - 用户ID（存入令牌的id字段）
          expires_delta - 令牌过期时间差，默认为15分钟
    返回：编码后的JWT令牌字符串
    """
    # 构建JWT载荷（payload）：包含用户名和用户ID
    encode = {"sub": username, "id": user_id}
    # 计算令牌过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta  # 使用指定的过期时间
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # 默认15分钟后过期
    # 将过期时间加入载荷
    encode.update({"exp": expire})
    # 使用密钥和算法对载荷进行编码，生成JWT字符串
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# ============================================
# 当前用户获取函数（全局依赖）
# ============================================

async def get_current_user(request: Request):
    """
    从请求的Cookie中解析JWT令牌，获取当前登录用户的信息
    参数：request - FastAPI请求对象
    返回：包含username和user_id的字典，未登录时返回None
    """
    try:
        # 从Cookie中获取名为access_token的JWT令牌
        token = request.cookies.get("access_token")
        if token is None:
            return None  # Cookie中无令牌，用户未登录
        # 使用密钥和算法解码JWT令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 从解码后的载荷中提取用户ID
        user_id = payload.get("id")
        # 从载荷中提取用户名
        username = payload.get("sub")
        # 验证载荷数据完整性
        if username is None or user_id is None:
            return None  # 载荷数据不完整，视为无效令牌
        # 返回当前用户信息字典
        return {"username": username, "user_id": user_id}
    except JWTError:
        # JWT解码失败（令牌过期、伪造、密钥不匹配等），返回None
        return None


# ============================================
# API路由：令牌获取（供OAuth2认证流程使用）
# ============================================

@router.post('/token', response_model=Token)
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2令牌登录接口（POST /auth/token）
    验证用户凭据，生成JWT令牌并设置到Cookie中
    参数：response - 响应对象，用于设置Cookie
          form_data - OAuth2表单数据（用户名和密码）
          db - 数据库会话依赖
    """
    # 调用authenticate_user验证用户名和密码
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        # 验证失败，抛出401未授权异常
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    # 设置令牌过期时间为60分钟
    token_expires = timedelta(minutes=60)
    # 生成JWT访问令牌
    token = create_access_token(user.username, user.id, expires_delta=token_expires)
    # 将JWT令牌设置到HTTP响应的Cookie中
    # httponly=True：Cookie不可被JavaScript访问，防止XSS攻击
    response.set_cookie(key="access_token", value=token, httponly=True)
    # 返回令牌信息到响应体
    return {"access_token": token, "token_type": "bearer"}


# ============================================
# 页面路由：登录
# ============================================

@router.get('/', response_class=HTMLResponse)
async def authentication_page(request: Request):
    """登录页面（GET /auth）：渲染登录表单HTML页面"""
    return templates.TemplateResponse(request, "login.html")


@router.post('/', response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    """
    处理登录表单提交（POST /auth）
    验证用户凭据，成功后重定向到待办事项列表页
    """
    try:
        # 创建LoginForm实例，从请求中提取表单数据
        form = LoginForm(request)
        await form.create_oauth_form()  # 异步解析表单
        # 创建重定向响应（登录成功后跳转到/todos页面）
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
        # 调用令牌生成接口进行用户验证并设置Cookie
        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)
        if not validate_user_cookie:
            # 验证失败，返回登录页面并显示错误消息
            msg = "用户名或密码错误"
            return templates.TemplateResponse(request, "login.html", {"msg": msg})
        return response  # 登录成功，执行重定向
    except HTTPException:
        # HTTP异常处理（如401未授权）
        msg = "登录失败，请重试"
        return templates.TemplateResponse(request, "login.html", {"msg": msg})


# ============================================
# 页面路由：登出
# ============================================

@router.get('/logout', response_class=HTMLResponse)
async def logout(request: Request):
    """
    登出处理（GET /auth/logout）
    删除访问令牌Cookie，返回登录页面
    """
    msg = "已成功登出"  # 登出成功提示消息
    response = templates.TemplateResponse(request, "login.html", {"msg": msg})
    # 删除客户端Cookie中的access_token，实现登出
    response.delete_cookie(key="access_token")
    return response


# ============================================
# 页面路由：注册
# ============================================

@router.get('/register', response_class=HTMLResponse)
async def register_page(request: Request):
    """注册页面（GET /auth/register）：渲染用户注册表单HTML页面"""
    return templates.TemplateResponse(request, "register.html")


@router.post('/register', response_class=HTMLResponse)
async def register(
    request: Request,
    email: str = Form(...),        # 邮箱（必填）
    username: str = Form(...),     # 用户名（必填）
    password: str = Form(...),     # 密码（必填）
    password2: str = Form(...),    # 确认密码（必填）
    firstname: str = Form(...),    # 名（必填）
    lastname: str = Form(...),     # 姓（必填）
    db: Session = Depends(get_db)  # 数据库会话依赖
):
    """
    处理注册表单提交（POST /auth/register）
    验证输入信息，创建新用户记录
    """
    # 检查用户名是否已存在
    validation1 = db.query(models.Users).filter(models.Users.username == username).first()
    # 检查邮箱是否已被注册
    validation2 = db.query(models.Users).filter(models.Users.email == email).first()

    # 验证注册条件：两次密码是否一致、用户名是否重复、邮箱是否重复
    if password != password2 or validation1 is not None or validation2 is not None:
        # 验证失败，返回注册页面并显示错误消息
        return templates.TemplateResponse(request, "register.html", {"msg": "注册信息无效，请检查输入"})

    # 创建新的用户模型实例
    user_model = Users(
        username=username,                              # 用户名
        email=email,                                    # 邮箱
        first_name=firstname,                           # 名
        last_name=lastname,                             # 姓
        hashed_password=bcrypt_context.hash(password),   # 加密后的密码
        role="user",                                    # 默认角色为普通用户
        is_active=True                                  # 默认激活状态
    )
    # 将新用户添加到数据库会话
    db.add(user_model)
    # 提交事务，将用户记录持久化到数据库
    db.commit()
    # 注册成功，返回登录页面并显示成功消息
    return templates.TemplateResponse(request, "login.html", {"msg": "用户注册成功，请登录"})






