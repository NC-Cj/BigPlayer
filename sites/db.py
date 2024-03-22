import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

_dp = os.path.dirname(os.path.abspath(__file__))
engine = create_engine(f'sqlite:///{_dp}/database.db')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()
