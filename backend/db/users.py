import os
from sqlalchemy import and_, select, update, insert, join
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from jose import jwt
import logging


from models.users import Users, Tokens
from models.databases import database
from config import pwd_context

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# получение пользовательского логгера и установка уровня логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# настройка обработчика и форматировщика в соответствии с нашими нуждами
handler = logging.FileHandler(f"logs/{__name__}.log", mode='w')
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
handler.setFormatter(formatter)
# добавление обработчика к логгеру
logger.addHandler(handler)

logger.info(f"Testing the custom logger for module {__name__}...")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username):
    query = (
            select(Users)
            .where(Users.username == username)
    )
    return await database.fetch_one(query)


async def get_user_by_id(user_id: int):
    try:
        query = (
                select(Users)
                .where(Users.id == user_id)
                .where(Users.is_active == True)
        )
        return await database.fetch_one(query)
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def get_user_by_name(username: str):
    try:
        query = (
                select(Users)
                .where(Users.username == username)
                .where(Users.is_active == True)
        )
        return await database.fetch_one(query)
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def check_user_token(user_id: int):
    try:
        query = select(Tokens).where(Tokens.user_id == user_id)
        return await database.fetch_one(query)
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def get_user_by_token(token: str):
    try:
        query = join([Tokens, Users]).select().where(
            and_(
                Tokens.access_token == token,
                Tokens.expires > datetime.now()
            )
        )
        return await database.fetch_one(query)
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(weeks=2)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_user_token(user_id: int, username, tz):
    data = {
                "sub": username,
                "user_id": user_id,
                "tz": tz,
            }
    access_token = await create_access_token(data)
    token_obj = await check_user_token(user_id)
    try:
        if token_obj:
            token = token_obj.access_token
            token_id = token_obj.id
            if token and token_id:
                query = (
                    update(Tokens)
                    .where(Tokens.id == token_id)
                    .values(
                        id=token_id,
                        access_token=access_token,
                        expires=datetime.utcnow() + timedelta(weeks=2),
                        user_id=user_id,
                    )
                    .returning(Tokens.access_token, Tokens.expires)
                )
            else:
                query = (
                    insert(Tokens)
                    .values(
                        access_token=access_token,
                        expires=datetime.utcnow() + timedelta(weeks=2),
                        user_id=user_id,
                    )
                    .returning(Tokens.access_token, Tokens.expires)
                )
        else:
            query = (
                insert(Tokens)
                .values(
                    access_token=access_token,
                    expires=datetime.utcnow() + timedelta(weeks=2),
                    user_id=user_id,
                )
                .returning(Tokens.access_token, Tokens.expires)
            )
        return await database.fetch_one(query)
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def create_user(username, password, tz):
    hashed_password = get_password_hash(password)
    query = insert(Users).values(
        username=username,
        hashed_password=hashed_password,
        role='users',
        is_active=True,
    )
    user_id = await database.execute(query)
    token = await create_user_token(user_id, username, tz)
    user = await get_user_by_name(username)
    if not token:
        return False
    else:
        token_dict = {"token": token["access_token"], "expires": token["expires"]}
        return {"id": user.id, "name": user.username, "is_active": True, "token": token_dict}
