# ============================================
# 数据库配置模块
# 功能：配置SQLAlchemy数据库引擎、会话管理和ORM基类
# 数据库类型：SQLite（本地文件存储）
# ============================================

# 导入SQLAlchemy的create_engine函数，用于创建数据库引擎
from sqlalchemy import create_engine
# 导入sessionmaker（会话工厂）和declarative_base（声明式ORM基类）
from sqlalchemy.orm import sessionmaker, declarative_base

#-----------------------------------postgresql数据库配置-----------------------------------
SQLALCHEMY_DATABASE_URL = (
    "postgresql://postgres.kyxzuqkklicrmrmujnll:lzy3604240993"
    "@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
    "?sslmode=require"
)
engine=create_engine(
    SQLALCHEMY_DATABASE_URL
)


#-----------------------------------sqlite数据库配置-----------------------------------
# SQLite数据库文件的连接URL，数据库文件为项目根目录下的todosapp.db
# 使用SQLite本地数据库，无需额外安装数据库服务
#SQLALCHEMY_DATABASE_URL="sqlite:///todosapp.db"

# 创建SQLAlchemy数据库引擎实例
# connect_args={"check_same_thread": False} 对于SQLite是必需的，
# 因为它允许FastAPI的多个线程同时访问SQLite数据库
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False}  # 允许多线程访问SQLite
# )




# 创建数据库会话工厂（SessionLocal）
# autocommit=False：不自动提交事务，需手动调用commit()
# autoflush=False：不自动刷新，需手动调用flush()
# bind=engine：将会话绑定到上面创建的数据库引擎
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建声明式ORM基类
# 所有数据模型类（如Users、Todos）都将继承这个Base类
# SQLAlchemy会通过Base.metadata自动管理表结构的创建和映射
Base = declarative_base()
