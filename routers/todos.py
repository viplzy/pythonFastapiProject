# ============================================
# 待办事项路由模块
# 功能：待办事项的增删改查（CRUD）及完成状态切换
# 路由前缀：/todos
# ============================================

# 导入HTTP状态码常量
from starlette import status
# 导入重定向响应类
from starlette.responses import RedirectResponse
# 导入FastAPI核心组件：Depends（依赖注入）、HTTPException（异常）、APIRouter（路由）、Request（请求对象）
from fastapi import Depends, HTTPException, APIRouter, Request

# 导入数据模型模块
import models
# 导入数据库引擎和会话工厂
from database import engine, SessionLocal
# 导入SQLAlchemy会话类
from sqlalchemy.orm import Session
# 导入Jinja2模板引擎
from fastapi.templating import Jinja2Templates
# 导入HTML响应类
from fastapi.responses import HTMLResponse
# 从认证模块导入get_current_user函数（用于获取当前登录用户）
from .auth import get_current_user

# ============================================
# 路由器配置
# ============================================
# 创建API路由器实例，所有路由都会自动添加 /todos 前缀
router = APIRouter(
    prefix='/todos',  # 路由URL前缀
    tags=['todos'],   # API文档分组标签
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
# 辅助函数：用户认证守卫
# ============================================

async def require_user(request: Request):
    """
    认证守卫函数：检查用户是否已登录
    未登录时重定向到登录页面
    返回：已登录的用户信息字典
    """
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
    return user


# ============================================
# 路由：查看所有待办事项（首页）
# ============================================

@router.get('/', response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    """
    获取当前用户的所有待办事项列表（GET /todos）
    仅显示当前登录用户的待办事项，实现数据隔离
    """
    # 验证用户登录状态
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
    # 查询当前用户的所有待办事项（按user_id过滤）
    todos = db.query(models.Todos).filter(models.Todos.user_id == user["user_id"]).all()
    # 渲染home.html模板，传入待办事项列表和用户信息
    return templates.TemplateResponse(request, "home.html", {"todos": todos, "user": user})


# ============================================
# 路由：添加待办事项页面
# ============================================

@router.get('/add-todo', response_class=HTMLResponse)
async def add_new_todo(request: Request):
    """
    新增待办事项页面（GET /todos/add-todo）
    渲染添加待办事项的表单页面
    """
    # 验证用户登录状态
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
    # 渲染add-todo.html模板
    return templates.TemplateResponse(request, "add-todo.html", {"user": user})


# ============================================
# 路由：创建待办事项（处理表单提交）
# ============================================

@router.post('/add-todo', response_class=HTMLResponse)
async def create_todo(request: Request, db: Session = Depends(get_db)):
    """
    创建新待办事项（POST /todos/add-todo）
    从HTML表单中提取数据，创建数据库记录
    """
    # 验证用户登录状态
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    # 异步获取表单数据（必须使用await）
    form = await request.form()
    # 从表单中提取各字段数据
    todo_title = form.get("title")                          # 待办事项标题
    todo_description = form.get("description")               # 待办事项描述
    todo_priority = int(form.get("priority", 1))             # 优先级（默认1）
    todo_complete = form.get("complete") == "on"             # 是否已完成（checkbox值）

    # 创建新的Todos模型实例
    new_todo = models.Todos(
        title=todo_title,
        description=todo_description,
        priority=todo_priority,
        complete=todo_complete,
        user_id=user.get('user_id')  # 关联当前登录用户
    )
    # 添加到数据库会话并提交
    db.add(new_todo)
    db.commit()
    # 创建成功后重定向到待办事项列表页
    return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)


# ============================================
# 路由：编辑待办事项页面
# ============================================

@router.get('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    """
    编辑待办事项页面（GET /todos/edit-todo/{todo_id}）
    根据ID获取待办事项，渲染编辑表单
    """
    # 验证用户登录状态
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    # 根据ID查询待办事项记录
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    # 渲染edit-todo.html模板，传入待办事项数据和用户信息
    return templates.TemplateResponse(request, "edit-todo.html", {"todo": todo, "user": user})


# ============================================
# 路由：更新待办事项（处理编辑表单提交）
# ============================================

@router.post('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def update_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    """
    更新待办事项（POST /todos/edit-todo/{todo_id}）
    根据ID查找并更新待办事项的各个字段
    """
    # 验证用户登录状态
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    # 异步获取表单数据
    form = await request.form()
    todo_title = form.get("title")                          # 更新后的标题
    todo_description = form.get("description")               # 更新后的描述
    todo_priority = int(form.get("priority", 1))             # 更新后的优先级
    todo_complete = form.get("complete") == "on"             # 更新后的完成状态

    # 根据ID查找待办事项记录
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo is None:
        # 记录不存在，抛出404异常
        raise HTTPException(status_code=404, detail="待办事项未找到")

    # 直接修改对象属性（SQLAlchemy会自动追踪变更）
    todo.title = todo_title
    todo.description = todo_description
    todo.priority = todo_priority
    todo.complete = todo_complete

    # 提交变更到数据库
    db.add(todo)
    db.commit()
    # 更新成功后重定向到待办事项列表页
    return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)


# ============================================
# 路由：删除待办事项
# ============================================

@router.get('/delete/{todo_id}', response_class=HTMLResponse)
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    """
    删除待办事项（GET /todos/delete/{todo_id}）
    仅允许删除当前用户自己的待办事项
    """
    # 验证用户登录状态
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    # 根据ID和当前用户ID双重条件查询，确保只能删除自己的待办事项
    todo = db.query(models.Todos).filter(
        models.Todos.id == todo_id,
        models.Todos.user_id == user.get('user_id')
    ).first()

    if todo is None:
        # 记录不存在或不属于当前用户，直接重定向
        return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)

    # 执行删除操作
    db.delete(todo)
    db.commit()
    # 删除成功后重定向到待办事项列表页
    return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)


# ============================================
# 路由：切换待办事项完成状态
# ============================================

@router.get('/complete/{todo_id}', response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    """
    切换待办事项的完成状态（GET /todos/complete/{todo_id}）
    将未完成标记为已完成，或撤销已完成状态
    """
    # 验证用户登录状态
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    # 根据ID查找待办事项记录
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo is None:
        return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)

    # 反转完成状态（True -> False 或 False -> True）
    todo.complete = not todo.complete

    # 提交变更到数据库
    db.add(todo)
    db.commit()
    # 操作成功后重定向到待办事项列表页
    return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)

