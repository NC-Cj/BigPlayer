import datetime

import pytz
from sqlalchemy import create_engine, Column, Integer, String, Index, DateTime, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base

_engine = create_engine('sqlite:///database.db')
_Session = sessionmaker(bind=_engine)
_session = _Session()
_Base = declarative_base()


class Boss(_Base):
    __tablename__ = 'boss'

    id = Column(Integer, primary_key=True)
    company = Column(String, unique=True)
    job_title = Column(String)
    salary = Column(String)
    address = Column(String)
    category = Column(String)
    link = Column(String)
    creation_time = Column(DateTime, server_default=datetime.datetime.now(pytz.timezone('Asia/Shanghai')).isoformat())

    # 添加索引
    __table_args__ = (
        UniqueConstraint('company'),
        Index('idx_company_name', 'company'),
        Index('idx_category', 'category')
    )


def setup():
    _Base.metadata.create_all(_engine)
    return _session


def insert(data):
    _session.add(Boss(**data))
    _session.commit()


if __name__ == '__main__':
    setup()
