# ============================================
# 用户管理路由模块
# 功能：用户密码修改
# 路由前缀：/users
# ============================================

# 导入HTTP状态码常量
from starlette import status
# 导入重定向响应类
from starlette.responses import RedirectResponse
# 导入FastAPI核心组件：Depends（依赖注入）、APIRouter（路由）、Request（请求对象）、Form（表单字段）
from fastapi import Depends, APIRouter, Request, Form

# 导入数据模型模块
import models
# 导入数据库引擎和会话工厂
from database import engine, SessionLocal
# 导入SQLAlchemy会话类
from sqlalchemy.orm import Session
# 导入Pydantic的BaseModel，用于数据验证模型
from pydantic import BaseModel
# 从认证模块导入必要的工具函数
from .auth import get_current_user, verify_password, get_password_hash
# 导入Jinja2模板引擎
from fastapi.templating import Jinja2Templates
# 导入HTML响应类
from fastapi.responses import HTMLResponse

# ============================================
# 路由器配置
# ============================================
# 创建API路由器实例，所有路由都会自动添加 /users 前缀
router = APIRouter(
    prefix='/users',  # 路由URL前缀
    tags=['users'],   # API文档分组标签
    responses={404: {'description': 'Not found'}}  # 默认404响应
)

# 确保数据库表结构已创建
models.Base.metadata.create_all(bind=engine)

# 初始化Jinja2模板引擎
templates = Jinja2Templates(directory="templates")


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
# Pydantic数据模型
# ============================================

class UserVerification(BaseModel):
    """
    用户密码修改验证模型（预留，供未来API接口使用）
    """
    username: str      # 用户名
    password: str      # 当前密码
    new_password: str  # 新密码


# ============================================
# 路由：修改密码页面
# ============================================

@router.get('/edit-password', response_class=HTMLResponse)
async def edit_password_page(request: Request):
    """
    修改密码页面（GET /users/edit-password）
    渲染密码修改表单页面
    """
    # 验证用户登录状态
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
    # 渲染edit-user-password.html模板，传入请求对象和用户信息
    return templates.TemplateResponse(request, 'edit-user-password.html', {'request': request, 'user': user})


# ============================================
# 路由：处理密码修改表单提交
# ============================================

@router.post('/edit-password', response_class=HTMLResponse)
async def change_password(
    request: Request,
    username: str = Form(...),     # 用户名（必填）
    password: str = Form(...),     # 旧密码（必填）
    password2: str = Form(...),    # 新密码（必填）
    db: Session = Depends(get_db)  # 数据库会话依赖
):
    """
    处理密码修改（POST /users/edit-password）
    验证旧密码正确性，更新为新密码
    """
    # 验证用户登录状态
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    # 从数据库中查找用户记录
    user_data = db.query(models.Users).filter(models.Users.username == username).first()

    # 默认错误消息
    msg = '用户名或密码无效'

    if user_data is not None:
        # 验证用户名和旧密码是否正确
        if username == user_data.username and verify_password(password, user_data.hashed_password):
            # 验证通过，更新为新密码的哈希值
            user_data.hashed_password = get_password_hash(password2)
            db.add(user_data)    # 将修改后的用户对象添加到会话
            db.commit()          # 提交事务，持久化到数据库
            msg = '密码更新成功'  # 成功消息
        else:
            msg = '用户名或密码无效'  # 验证失败消息

    # 返回密码修改页面，并显示操作结果消息
    return templates.TemplateResponse(request, 'edit-user-password.html', {
        'request': request,
        'user': user,
        'msg': msg
    })



