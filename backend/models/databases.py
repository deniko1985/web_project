import os
# import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
# import databases
import redis

from dotenv import load_dotenv

load_dotenv()

# metadata = sqlalchemy.MetaData()

DATABASE_URL = os.getenv("DATABASE_URL")
# database = databases.Database(DATABASE_URL)
# engine = sqlalchemy.create_engine(
#     DATABASE_URL
# )
# metadata.create_all(engine)

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    expire_on_commit=False,
    class_=AsyncSession,
    bind=engine,
)

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")
REDIS_DECODE_RESPONSES = os.getenv("REDIS_DECODE_RESPONSES")

redis_cli = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=REDIS_DECODE_RESPONSES
)
