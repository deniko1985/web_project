import sqlalchemy
import databases

metadata = sqlalchemy.MetaData()

postgres_ip = 'postgres'
postgres_port: 5432
postgres_name = 'postgres'
postgres_password = 'postgres'
postgres_db = "web_project"

DATABASE_URL = "postgresql://postgres:postgres@postgres/web_project"
database = databases.Database(DATABASE_URL)
engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)
