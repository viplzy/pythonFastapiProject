# ============================================
# 数据模型定义模块
# 功能：定义users表和todos表的ORM模型结构
# 使用SQLAlchemy ORM进行数据库表映射
# ============================================

# 从database模块导入声明式ORM基类Base
from database import Base
# 导入SQLAlchemy列类型和约束定义
# Column：定义表中的列
# Integer：整数类型
# String：字符串类型
# Boolean：布尔类型
# ForeignKey：外键约束
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


# ============================================
# 用户数据模型（Users表）
# 映射到数据库中的users表，存储用户账户信息
# ============================================
class Users(Base):
    # 指定该模型对应的数据库表名
    __tablename__ = "users"

    # 用户唯一标识ID，主键字段，自动创建索引以加速查询
    id = Column(Integer, primary_key=True, index=True)

    # 用户登录名，设置为唯一约束，确保用户名不重复
    username = Column(String, unique=True)

    # 用户邮箱地址，设置为唯一约束，确保邮箱不重复
    email = Column(String, unique=True)

    # 用户的名字（名）
    first_name = Column(String)

    # 用户的姓氏（姓）
    last_name = Column(String)

    # 加密后的密码哈希值，不存储明文密码，保障安全性
    hashed_password = Column(String)

    # 账户激活状态，默认为True（激活状态）
    is_active = Column(Boolean, default=True)

    # 用户角色标识，如"user"（普通用户）或"admin"（管理员）
    role = Column(String)

    # 备用字段：电话号码（当前已注释，需要时可取消注释启用）
    # phone_number = Column(String)


# ============================================
# 待办事项数据模型（Todos表）
# 映射到数据库中的todos表，存储用户的待办事项
# ============================================
class Todos(Base):
    # 指定该模型对应的数据库表名
    __tablename__ = "todos"

    # 待办事项唯一标识ID，主键字段，自动创建索引以加速查询
    id = Column(Integer, primary_key=True, index=True)

    # 待办事项的标题（简短描述）
    title = Column(String)

    # 待办事项的详细描述信息
    description = Column(String)

    # 待办事项的优先级（数字越大优先级越高，范围1-5）
    priority = Column(Integer)

    # 完成状态标识，默认为False（未完成），True表示已完成
    complete = Column(Boolean, default=False)

    # 关联用户ID，外键指向users表的id字段
    # 用于标识该待办事项属于哪个用户
    user_id = Column(Integer, ForeignKey("users.id"))
