import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

metadata = sqlalchemy.MetaData()

Base = declarative_base(metadata=metadata)


class Budget(Base):
    __tablename__ = "budget"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    username = Column(String(100))
    income = Column(Float)
    expense = Column(Float)
    comment = Column(String())
    date = Column(DateTime())
