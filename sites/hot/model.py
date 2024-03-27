import datetime

import pytz
from sqlalchemy import Column, Integer, String, Index, DateTime, UniqueConstraint
from sqlalchemy.exc import SQLAlchemyError

from core.utils import logger
from sites.db import Base, session, engine


class Hot(Base):
    __tablename__ = 'hot'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    link = Column(String, unique=True, nullable=False)
    platform = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=datetime.datetime.now(pytz.timezone('Asia/Shanghai')).isoformat())

    # 添加索引
    __table_args__ = (
        UniqueConstraint('link'),
        Index('idx_platform', 'platform'),
        Index('idx_link', 'link'),
    )


def setup():
    Base.metadata.create_all(engine)
    return session


def insert(data):
    try:
        session.add(Hot(**data))
        session.commit()
    except SQLAlchemyError:
        logger.warning(f"Error inserting: {data}")
        session.rollback()
