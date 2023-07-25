import os
import sqlalchemy
import databases

from dotenv import load_dotenv

load_dotenv()

metadata = sqlalchemy.MetaData()

DATABASE_URL = os.getenv("SQLALCHEMY_URL_TESTING")
database = databases.Database(DATABASE_URL)
engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)
