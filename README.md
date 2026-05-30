
### 1、运行以下命令，根据项目自动生成依赖配置文件requirements.txt
```
pip3 freeze > requirements.txt
```
### 2、将最新的内容部署到render(https://dashboard.render.com/project/prj-d72jea4r85hc73drb77g)
### 3、在https://supabase.com/创建数据库
### 4、更改database.py文件中的相关配置
```





# FastAPI 全栈待办事项应用

基于 **FastAPI + SQLAlchemy + Jinja2 + PostgreSQL** 构建的全栈待办事项（Todo）管理应用，支持用户注册、登录鉴权、密码修改、待办事项增删改查及完成状态切换等功能。

---

## 项目结构

```
pythonFastapiProject/
├── main.py                  # 应用主入口，创建 FastAPI 实例、注册路由、挂载静态文件
├── database.py              # 数据库配置（SQLAlchemy 引擎、会话工厂、ORM 基类）
├── models.py                # 数据模型定义（Users 表、Todos 表）
├── requirements.txt         # Python 依赖列表
├── alembic.ini              # Alembic 数据库迁移配置
├── routers/
│   ├── auth.py              # 认证路由：登录、注册、登出、JWT 令牌管理
│   ├── todos.py             # 待办事项路由：增删改查、完成状态切换
│   └── users.py             # 用户管理路由：密码修改
├── templates/               # Jinja2 HTML 模板
│   ├── layout.html          # 基础布局模板
│   ├── navbar.html          # 导航栏模板
│   ├── login.html           # 登录页面
│   ├── register.html        # 注册页面
│   ├── home.html            # 待办事项列表页（首页）
│   ├── add-todo.html        # 新增待办事项页
│   ├── edit-todo.html       # 编辑待办事项页
│   └── edit-user-password.html  # 修改密码页
├── static/
│   └── todo/css/base.css    # 静态样式文件
├── migrations/              # Alembic 数据库迁移脚本
│   ├── env.py               # 迁移环境配置
│   ├── script.py.mako       # 迁移脚本模板
│   └── versions/            # 迁移版本文件
└── todosapp.db              # SQLite 本地数据库文件（备用）
```

---

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| Web 框架 | FastAPI | 高性能异步 Python Web 框架 |
| ORM | SQLAlchemy 2.x | 数据库对象关系映射 |
| 数据库 | PostgreSQL (Supabase) | 生产环境使用 Supabase 托管的 PostgreSQL |
| 备用数据库 | SQLite | 本地开发可用 SQLite |
| 模板引擎 | Jinja2 | 服务端 HTML 渲染 |
| 密码加密 | passlib + bcrypt | 密码哈希加密与验证 |
| 认证方案 | JWT (python-jose) | 基于 Cookie 的 JWT 令牌认证 |
| 数据库迁移 | Alembic | 数据库 schema 版本管理 |
| ASGI 服务器 | Uvicorn | 高性能异步服务器 |

---

## 快速开始

### 1. 环境准备

确保已安装 Python 3.9+，然后克隆项目并安装依赖：

```bash
# 克隆项目
git clone https://github.com/viplzy /pythonFastapiProject.git
cd pythonFastapiProject

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置

项目默认使用 **PostgreSQL (Supabase)**，也可切换为本地 SQLite。

#### 方式一：使用 PostgreSQL（推荐，生产环境）

修改 `database.py` 中的连接字符串：

```python
SQLALCHEMY_DATABASE_URL = (
    "postgresql://<用户名>:<密码>@<主机>:<端口>/<数据库名>"
    "?sslmode=require"
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
```

#### 方式二：使用 SQLite（本地开发）

将 `database.py` 中的 PostgreSQL 配置注释掉，取消 SQLite 配置的注释：

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///todosapp.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 多线程必需
)
```

### 3. 数据库迁移（使用 Alembic）

如果使用 PostgreSQL 并需要对数据库 schema 进行版本管理：

```bash
# 初始化 Alembic 迁移环境（首次）
alembic init migrations

# 配置 migrations/env.py，添加：
# from models import Base
# target_metadata = Base.metadata

# 修改 alembic.ini 中的 sqlalchemy.url 为数据库连接字符串

# 根据模型变更自动生成迁移脚本
alembic revision --autogenerate -m "描述信息"

# 执行迁移，应用到数据库
alembic upgrade head
```

### 4. 启动应用

```bash
# 开发模式（自动热重载）
uvicorn main:app --reload

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000
```

启动后访问：
- 应用首页：http://127.0.0.1:8000/
- API 文档（Swagger）：http://127.0.0.1:8000/docs
- API 文档（ReDoc）：http://127.0.0.1:8000/redoc

---

## 功能详解与使用步骤

### 一、用户注册

**访问路径：** `GET /auth/register`

**功能说明：** 新用户通过填写注册表单创建账户。

**使用步骤：**

1. 在浏览器访问 `/auth/register` 打开注册页面
2. 填写以下必填信息：
   - **用户名 (username)** — 必须全局唯一，不可与已注册用户重复
   - **邮箱 (email)** — 必须全局唯一，不可与已注册邮箱重复
   - **密码 (password)** — 登录密码
   - **确认密码 (password2)** — 必须与密码一致
   - **名 (firstname)** — 用户的名字
   - **姓 (lastname)** — 用户的姓氏
3. 提交表单 (`POST /auth/register`)

**注册校验规则：**

| 校验项 | 规则 | 失败提示 |
|--------|------|----------|
| 用户名唯一性 | 数据库中 `users.username` 不可重复 | 注册信息无效，请检查输入 |
| 邮箱唯一性 | 数据库中 `users.email` 不可重复 | 注册信息无效，请检查输入 |
| 两次密码一致 | `password` 必须等于 `password2` | 注册信息无效，请检查输入 |

**注册成功后：**
- 密码通过 `bcrypt` 加密存储（非明文），存储在 `users.hashed_password` 字段
- 新用户默认角色为 `user`，默认激活状态为 `True`
- 自动跳转到登录页面，提示"用户注册成功，请登录"

---

### 二、用户登录

**访问路径：** `GET /auth` → 登录页面

**功能说明：** 已注册用户通过用户名和密码登录系统，获取 JWT 令牌。

**使用步骤：**

1. 在浏览器访问 `/auth` 打开登录页面
2. 输入 **用户名** 和 **密码**
3. 提交表单 (`POST /auth`)

**登录鉴权流程：**

```
用户提交登录表单
    │
    ▼
LoginForm.create_oauth_form()  ←── 从请求中异步解析表单数据
    │
    ▼
authenticate_user(username, password, db)
    │
    ├── db.query(Users).filter(username == username).first()
    │       │
    │       └── 用户不存在 → 返回 False → 登录失败
    │
    ├── verify_password(plain_password, hashed_password)
    │       │
    │       └── 密码不匹配 → 返回 False → 登录失败
    │
    └── 验证通过 → 返回 user 对象
            │
            ▼
create_access_token(username, user_id, expires_delta)
    │
    ├── 构建 JWT 载荷: {"sub": username, "id": user_id, "exp": 过期时间}
    ├── 使用 SECRET_KEY + HS256 算法签名
    └── 生成 JWT 令牌字符串
            │
            ▼
response.set_cookie("access_token", token, httponly=True)
    │
    ├── httponly=True → Cookie 不可被 JavaScript 读取，防止 XSS 攻击
    └── 令牌有效期：60 分钟
            │
            ▼
重定向到 /todos（待办事项首页）
```

**JWT 令牌说明：**

| 配置项 | 值 | 说明 |
|--------|------|------|
| 签名密钥 | `SECRET_KEY`（默认 `197b2c37`，建议通过环境变量设置） | 用于签署和验证 JWT |
| 签名算法 | HS256 | HMAC-SHA256 对称加密 |
| 令牌有效期 | 60 分钟 | 超时后需重新登录 |
| 存储方式 | HTTP Cookie (`access_token`) | httponly=True，防止 XSS |
| 载荷字段 | `sub`（用户名）、`id`（用户ID）、`exp`（过期时间） | 标准 JWT 声明 |

---

### 三、用户登出

**访问路径：** `GET /auth/logout`

**功能说明：** 清除客户端的 JWT 令牌 Cookie，终止当前会话。

**使用步骤：**

1. 点击导航栏中的"登出"按钮或访问 `/auth/logout`
2. 系统自动删除浏览器中名为 `access_token` 的 Cookie
3. 页面跳转到登录页，显示"已成功登出"提示

---

### 四、待办事项管理（需登录）

所有待办事项功能的访问均受登录保护。未登录用户访问时，`get_current_user()` 返回 `None`，系统自动重定向到登录页面 `/auth`。

#### 4.1 查看待办事项列表

**访问路径：** `GET /todos`

**功能说明：** 显示当前登录用户的所有待办事项，实现数据隔离（每个用户只能看到自己的待办事项）。

**鉴权流程：**
1. 从 Cookie 中读取 `access_token`
2. 使用 `SECRET_KEY` 和 `HS256` 算法解码 JWT 令牌
3. 提取 `sub`（用户名）和 `id`（用户ID）
4. 根据 `user_id` 过滤查询待办事项

#### 4.2 新增待办事项

**访问路径：** `GET /todos/add-todo` → 新增页面

**使用步骤：**
1. 访问 `/todos/add-todo` 打开新增表单
2. 填写以下字段：
   - **标题 (title)** — 待办事项标题
   - **描述 (description)** — 详细说明
   - **优先级 (priority)** — 数字，默认 1，范围 1-5
   - **是否完成 (complete)** — 复选框
3. 提交表单 (`POST /todos/add-todo`)
4. 创建成功后自动重定向回待办事项列表页

#### 4.3 编辑待办事项

**访问路径：** `GET /todos/edit-todo/{todo_id}` → 编辑页面

**使用步骤：**
1. 在列表页点击待办事项的"编辑"按钮
2. 修改标题、描述、优先级、完成状态
3. 提交表单 (`POST /todos/edit-todo/{todo_id}`)
4. 更新成功后自动重定向回列表页

#### 4.4 删除待办事项

**访问路径：** `GET /todos/delete/{todo_id}`

**功能说明：** 删除指定的待办事项。采用**双重条件校验**——只能删除当前登录用户自己的待办事项（同时匹配 `todo_id` 和 `user_id`），防止越权删除。

#### 4.5 切换完成状态

**访问路径：** `GET /todos/complete/{todo_id}`

**功能说明：** 反转待办事项的完成状态（未完成 → 已完成，已完成 → 未完成）。

---

### 五、修改密码（需登录）

**访问路径：** `GET /users/edit-password` → 修改密码页面

**使用步骤：**

1. 访问 `/users/edit-password` 打开修改密码表单
2. 填写以下字段：
   - **用户名 (username)** — 确认当前用户名
   - **旧密码 (password)** — 当前使用的密码
   - **新密码 (password2)** — 要设置的新密码
3. 提交表单 (`POST /users/edit-password`)

**校验流程：**

```
提交修改密码表单
    │
    ▼
get_current_user(request)  ←── 验证当前登录状态
    │
    ├── 未登录 → 重定向到 /auth（登录页）
    │
    ▼
db.query(Users).filter(u