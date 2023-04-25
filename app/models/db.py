import sqlalchemy
import databases
# import psycopg2
# from sqlalchemy import create_engine
# from conf_read import postgres_name, postgres_password, postgres_ip, postgres_port, postgres_db

metadata = sqlalchemy.MetaData()

postgres_ip = 'postgres'
postgres_port: 5432
postgres_name = 'postgres'
postgres_password = 'postgres'
postgres_db = "web_project"

DATABASE_URL = "postgresql://postgres:postgres@postgres/web_project"
# DATABASE_URL = "postgresql://postgres:postgres@localhost:5732/web_project"
# DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/vc_sa_test"
# DATABASE_URL = "postgresql://" + str(postgres_name) + ":" + str(postgres_password) + "@" + str(postgres_ip) + ":"\
#               + str(postgres_port) + "/" + str(postgres_db)
database = databases.Database(DATABASE_URL)
engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)
# engine.connect()
print(engine, metadata)
