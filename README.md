### 1、创建templates目录,在目录下创建home.html文件
### 2、安装aiofiles、jinja2(可以在html中编写pyrhon语法)
### 3、在todos.py导入
```commandline
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
```
### 4、创建static目录，存储js和css文件
### 5、在main.py文件中导入css
```commandline
from starlette.staticfiles import StaticFiles
app.mount("/static",StaticFiles(directory="static"),name="static")
```
### 6、将css导入html
# TodoApp - 全栈待办事项管理应用

一个基于 **FastAPI** + **SQLAlchemy** + **Jinja2** + **Bootstrap 5** 构建的全栈Web应用，支持用户注册/登录、待办事项的增删改查、优先级管理和完成状态切换。

---

## 项目简介

TodoApp 是一个功能完整的待办事项管理系统，用户可以通过浏览器访问。系统采用前后端一体化架构，后端使用 FastAPI 提供 RESTful API，前端使用 Jinja2 模板引擎配合 Bootstrap 5 实现响应式UI。

### 核心功能

| 功能模块 | 说明 |
|---------|------|
| 用户认证 | 注册、登录、登出，基于 JWT 令牌 + Cookie 的身份验证 |
| 密码安全 | bcrypt 加密存储，支持修改密码 |
| 待办事项管理 | 创建、查看、编辑、删除待办事项 |
| 完成状态 | 标记完成/撤销完成，已完成事项显示删除线 |
| 优先级 | 5级优先级设置（1-5），编辑时自动回填 |
| 数据隔离 | 每个用户只能查看和管理自己的待办事项 |
| 响应式设计 | 基于 Bootstrap 5，适配PC端和移动端 |

---

## 项目结构

```
07.全栈应用/
├── main.py                  # FastAPI应用入口，路由注册，静态文件挂载
├── database.py              # 数据库配置（SQLite + SQLAlchemy）
├── models.py                # ORM数据模型定义（Users、Todos）
├── routers/                 # 路由模块目录
│   ├── auth.py              # 认证路由（登录/注册/登出/JWT令牌）
│   ├── todos.py             # 待办事项路由（CRUD + 完成切换）
│   └── users.py             # 用户管理路由（密码修改）
├── templates/               # Jinja2 HTML模板目录
│   ├── layout.html          # 基础布局模板（CSS/JS框架引入）
│   ├── navbar.html          # 导航栏组件
│   ├── login.html           # 登录页面
│   ├── register.html        # 注册页面
│   ├── home.html            # 待办事项列表页（首页）
│   ├── add-todo.html        # 新增待办事项页面
│   ├── edit-todo.html       # 编辑待办事项页面
│   └── edit-user-password.html  # 修改密码页面
├── static/todo/             # 静态资源目录
│   ├── css/
│   │   └── base.css         # 全局自定义样式表
│   └── js/                  # JavaScript文件目录（预留）
├── todosapp.db              # SQLite数据库文件（自动生成）
└── README.md                # 项目说明文档
```

---

## 快速开始

### 环境要求

- Python 3.8+
- pip 包管理器

### 安装依赖

```bash
pip install fastapi uvicorn jinja2 aiofiles python-multipart sqlalchemy passlib[bcrypt] python-jose[cryptography]
```

### 启动应用

```bash
cd "D:\study\pythonProject\第五章：FastApi使用\07.全栈应用"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

启动成功后访问：**http://localhost:8000**

### 首次使用

1. 打开浏览器访问 `http://localhost:8000`，自动跳转到登录页
2. 点击「没有账号？去注册」创建新账户
3. 填写注册信息后登录
4. 在主页面点击「新增待办事项」开始使用

---

## API 接口一览

### 认证模块 `/auth`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/auth` | 登录页面 |
| POST | `/auth` | 处理登录表单 |
| GET | `/auth/register` | 注册页面 |
| POST | `/auth/register` | 处理注册表单 |
| GET | `/auth/logout` | 登出（清除Cookie） |
| POST | `/auth/token` | API令牌获取（OAuth2） |

### 待办事项模块 `/todos`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/todos` | 待办事项列表（首页） |
| GET | `/todos/add-todo` | 新增待办事项页面 |
| POST | `/todos/add-todo` | 创建待办事项 |
| GET | `/todos/edit-todo/{id}` | 编辑待办事项页面 |
| POST | `/todos/edit-todo/{id}` | 更新待办事项 |
| GET | `/todos/delete/{id}` | 删除待办事项 |
| GET | `/todos/complete/{id}` | 切换完成状态 |

### 用户模块 `/users`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/users/edit-password` | 修改密码页面 |
| POST | `/users/edit-password` | 处理密码修改 |

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| Web框架 | FastAPI | 高性能异步Python Web框架 |
| ASGI服务器 | Uvicorn | 轻量级ASGI服务器 |
| 模板引擎 | Jinja2 | Python模板引擎，支持模板继承 |
| ORM | SQLAlchemy | 数据库对象关系映射 |
| 数据库 | SQLite | 轻量级文件数据库 |
| 密码加密 | bcrypt (passlib) | 安全的密码哈希算法 |
| 身份认证 | JWT (python-jose) | JSON Web Token 令牌认证 |
| 前端框架 | Bootstrap 5.3 | 响应式CSS框架 |
| 样式 | 自定义CSS | 导航栏主题色、删除线等 |

---

## 设计要点

### 安全性
- 密码使用 **bcrypt** 哈希加密存储，不保存明文
- JWT令牌存储在 **HttpOnly Cookie** 中，防止XSS攻击
- 每个请求通过Cookie中的JWT令牌验证用户身份
- 用户只能操作自己的待办事项（基于 `user_id` 过滤）

### 模板继承
- `layout.html` 作为基础模板，定义公共的HTML结构和资源引入
- 各页面通过 `{% extends "layout.html" %}` 继承布局
- `navbar.html` 作为导航栏组件被 `{% include %}` 引入
- 通过 `{% block content %}` 实现内容区域的自定义

### 数据流

```
浏览器 → FastAPI路由 → 依赖注入(get_db) → SQLAlchemy Session → SQLite数据库
                                                ↓
用户认证 ← JWT Cookie ← get_current_user() ← 请求Cookie
```

---

## 数据库模型

### Users 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | 主键、索引 | 用户唯一ID |
| username | String | 唯一 | 登录用户名 |
| email | String | 唯一 | 邮箱地址 |
| first_name | String | - | 名 |
| last_name | String | - | 姓 |
| hashed_password | String | - | bcrypt加密密码 |
| is_active | Boolean | 默认True | 账户激活状态 |
| role | String | - | 用户角色 |

### Todos 表
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | 主键、索引 | 事项唯一ID |
| title | String | - | 事项标题 |
| description | String | - | 详细描述 |
| priority | Integer | - | 优先级(1-5) |
| complete | Boolean | 默认False | 完成状态 |
| user_id | Integer | 外键→users.id | 所属用户 |

---

## 浏览器兼容性

- Chrome / Edge / Firefox / Safari 最新版本
- 支持移动端响应式布局（Bootstrap 5 网格系统）

---

> 提示：生产环境部署时请务必修改 `SECRET_KEY` 环境变量，并使用 PostgreSQL 等生产级数据库替代 SQLite。
