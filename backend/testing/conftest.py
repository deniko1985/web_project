import os
import sys

# import pytest


from alembic import command
from alembic.config import Config
from sqlalchemy_utils import create_database, drop_database

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from models.db import database

# Устанавливаем `os.environ`, чтобы использовать тестовую БД
# os.environ['TESTING'] = 'True'


# @pytest.fixture(scope="module")
def temp_db():
    create_database(database.SQLALCHEMY_URL_TESTING)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
    command.upgrade(alembic_cfg, "head")

    try:
        yield database.SQLALCHEMY_URL_TESTING
    finally:
        drop_database(database.SQLALCHEMY_URL_TESTING)
