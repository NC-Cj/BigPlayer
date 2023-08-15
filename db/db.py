import datetime

import pytz
from sqlalchemy import create_engine, Column, Integer, String, Index, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建SQLite数据库引擎
engine = create_engine('sqlite:///database.db')

# 创建会话工厂
Session = sessionmaker(bind=engine)
session = Session()

# 创建基本模型类
Base = declarative_base()


# 定义数据表模型类
class Boss(Base):
    __tablename__ = 'boss'

    id = Column(Integer, primary_key=True)
    company_name = Column(String, unique=True)
    job_name = Column(String)
    salary = Column(String)
    address = Column(String)
    category = Column(String)
    creation_time = Column(DateTime, server_default=datetime.datetime.now(pytz.timezone('Asia/Shanghai')).isoformat())


    # 添加索引
    __table_args__ = (
        UniqueConstraint('company_name'),
        Index('idx_company_name', 'company_name'),
        Index('idx_category', 'category')
    )


# 创建数据表
Base.metadata.create_all(engine)
