import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, ARRAY, Text
from sqlalchemy.ext.declarative import declarative_base

metadata = sqlalchemy.MetaData()

Base = declarative_base(metadata=metadata)


class Notes(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    username = Column(String(100))
    name_notes = Column(String(100), index=True)
    text_notes = Column(Text, index=True)
    favourites = Column(String(), default="off")
    date = Column(DateTime())
    lang = Column(String())
    keywords = Column(ARRAY(item_type=sqlalchemy.String()))
