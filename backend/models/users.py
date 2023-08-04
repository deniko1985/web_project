import sqlalchemy
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

metadata = sqlalchemy.MetaData()

Base = declarative_base(metadata=metadata)


class Users(Base):
    __tablename__ = "users"
    id = Column(
        Integer,
        Sequence('users_id_seq', start=1, increment=1),
        primary_key=True,
        autoincrement=True,
    )
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String())
    is_active = Column(Boolean(), server_default=sqlalchemy.sql.expression.true(), nullable=False)
    role = Column(String())
    company_id = Column(Integer)
    email = Column(String())


class Tokens(Base):
    __tablename__ = "tokens"
    id = Column("id", Integer, primary_key=True)
    access_token = Column(String(256), unique=True, nullable=False, index=True,)
    expires = Column(DateTime())
    user_id = Column(ForeignKey("users.id"))
