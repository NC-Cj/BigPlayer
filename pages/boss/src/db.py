import datetime

import pytz
from sqlalchemy import create_engine, Column, Integer, String, Index, DateTime, UniqueConstraint
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base

from core.utils import logger

db_file_path = "../database.db"

_engine = create_engine(f'sqlite:///{db_file_path}')
_Session = sessionmaker(bind=_engine)
_session = _Session()
_Base = declarative_base()


class Boss(_Base):
    __tablename__ = 'boss'

    id = Column(Integer, primary_key=True)
    company = Column(String)
    job_title = Column(String, nullable=False)
    min_salary = Column(Integer, nullable=False)
    max_salary = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    category = Column(String, nullable=False)
    path = Column(String, unique=True, nullable=False)
    city = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=datetime.datetime.now(pytz.timezone('Asia/Shanghai')).isoformat())

    # 添加索引
    __table_args__ = (
        UniqueConstraint('path'),
        Index('idx_path', 'path'),
        Index('idx_address', 'address'),
        Index('idx_city', 'city'),
        Index('idx_category', 'category')
    )


def setup():
    _Base.metadata.create_all(_engine)
    return _session


def insert(data):
    try:
        _session.add(Boss(**data))
        _session.commit()
    except SQLAlchemyError:
        logger.warning(f"Error inserting: {data}")
        _session.rollback()


if __name__ == '__main__':
    setup()
