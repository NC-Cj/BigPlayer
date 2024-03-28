import datetime

import pytz
from loguru import logger
from sqlalchemy import Column, String, Integer, DateTime, UniqueConstraint, Index
from sqlalchemy.exc import SQLAlchemyError

from sites.db import Base, engine, session


class ApplyJob(Base):
    __tablename__ = 'apply_job'

    id = Column(Integer, primary_key=True)
    company = Column(String)
    job_title = Column(String, nullable=False)
    min_salary = Column(Integer, nullable=False)
    max_salary = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    category = Column(String, nullable=False)
    path = Column(String, unique=True, nullable=False)
    city = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=datetime.datetime.now(pytz.timezone('Asia/Shanghai')).isoformat())

    # 添加索引
    __table_args__ = (
        UniqueConstraint('path'),
        Index('idx_path', 'path'),
        Index('idx_address', 'address'),
        Index('idx_city', 'city'),
        Index('idx_category', 'category'),
        Index('idx_platform', 'platform')
    )


def setup():
    Base.metadata.create_all(engine)


def insert(data):
    try:
        session.add(ApplyJob(**data))
        session.commit()
    except SQLAlchemyError:
        logger.warning(f"Error inserting: {data}")
        session.rollback()


def company_exists(path):
    return session.query(ApplyJob.id).filter(ApplyJob.path == path).first()
