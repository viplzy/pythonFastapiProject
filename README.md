### 1、运行以下命令，根据项目自动生成依赖配置文件requirements.txt
```
pip3 freeze > requirements.txt
```
### 2、将最新的内容部署到render(https://dashboard.render.com/project/prj-d72jea4r85hc73drb77g)
### 3、在https://supabase.com/创建数据库
### 4、更改database.py文件中的相关配置
```
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:lzy3604240993@db.kyxzuqkklicrmrmujnll.supabase.co:5432/postgres"
engine=create_engine(SQLALCHEMY_DATABASE_URL)
```
### 5、部署时报错

### 6、数据库迁移：添加phone_number字段
1. 初始化Alembic迁移环境
```bash
alembic init migrations
```
- 在models.py中的Users类中添加phone_number字段

2. 配置数据库连接
- 修改alembic.ini中的sqlalchemy.url为PostgreSQL连接字符串
```ini
sqlalchemy.url = postgresql://postgres.kyxzuqkklicrmrmujnll:lzy3604240993@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require
```

3. 配置迁移环境
- 修改migrations/env.py，添加：
```python
from models import Base
target_metadata = Base.metadata
```

4. 修改模型
- 取消models.py中Users类的phone_number字段注释

5. 创建迁移脚本
```bash
alembic revision --autogenerate -m "add phone_number to users table"
```

6. 应用迁移
```bash
alembic upgrade head
```