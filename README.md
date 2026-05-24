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