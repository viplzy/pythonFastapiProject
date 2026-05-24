# ============================================
# FastAPI 全栈待办事项应用 —— 主入口模块
# 功能：创建FastAPI应用实例、注册路由、挂载静态文件、配置数据库
# 启动命令：uvicorn main:app --reload
# ============================================

# 导入FastAPI核心框架类，用于创建Web应用实例
from fastapi import FastAPI

# 导入数据模型模块，包含Users和Todos的ORM模型定义
import models

# 从database模块导入数据库引擎实例
from database import engine

# 导入三个路由模块：auth（认证）、todos（待办事项）、users（用户管理）
from routers import auth, todos, users

# 导入StaticFiles用于挂载静态资源目录（CSS、JS、图片等）
from starlette.staticfiles import StaticFiles

# 导入HTTP状态码常量模块
from starlette import status

# 导入RedirectResponse用于URL重定向
from starlette.responses import RedirectResponse

# 创建FastAPI应用实例（整个Web应用的核心对象）
app = FastAPI()

# 根据ORM模型自动创建所有数据库表结构
# bind=engine：指定使用上面创建的数据库引擎
# 如果表已存在则不会重复创建（安全操作）
models.Base.metadata.create_all(bind=engine)

# 挂载静态文件目录，将/static路径映射到项目中的static文件夹
# 例如：访问 /static/todo/css/base.css 对应文件 static/todo/css/base.css
app.mount("/static", StaticFiles(directory="static"), name="static")


# 根路径路由：访问 / 时自动重定向到 /todos（待办事项列表页）
@app.get("/")
async def root():
    # HTTP 302 临时重定向，将根路径请求转发到待办事项主页
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


# 注册认证路由模块到应用中（包含登录、注册、登出等功能）
# 路由前缀 /auth 已在auth.py中通过APIRouter的prefix参数设置
app.include_router(auth.router)

# 注册待办事项路由模块到应用中（包含增删改查等功能）
# 路由前缀 /todos 已在todos.py中设置
app.include_router(todos.router)

# 注册用户管理路由模块到应用中（包含密码修改等功能）
# 路由前缀 /users 已在users.py中设置
app.include_router(users.router)
