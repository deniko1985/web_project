import os
from sqlalchemy import and_, select, update, insert, join
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from jose import jwt
import logging


from models.users import Users, Tokens
# from models.dbs import db
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


async def get_user(db: AsyncSession, username):
    query = await db.execute(
            select(Users)
            .where(Users.username == username)
    )
    return query.scalar()


async def get_user_by_id(db: AsyncSession, user_id: int):
    try:
        query = await db.execute(
                select(Users)
                .where(Users.id == user_id)
                .where(Users.is_active == True)
        )
        return query.scalar()
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def get_user_by_name(db: AsyncSession, username: str):
    try:
        query = await db.execute(
                select(Users)
                .where(Users.username == username)
                .where(Users.is_active == True)
        )
        return query.scalar()
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def check_user_token(db: AsyncSession, user_id: int):
    try:
        print(user_id)
        query = await db.execute(select(Tokens).where(Tokens.user_id == user_id))
        return query.scalar()
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def get_user_by_token(db: AsyncSession, token: str):
    try:
        query = await db.execute(join([Tokens, Users]).select().where(
            and_(
                Tokens.access_token == token,
                Tokens.expires > datetime.now()
            )
        ))
        return query.scalar()
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def create_access_token(db: AsyncSession, data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(weeks=2)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_user_token(db: AsyncSession, user_id: int, username, tz):
    data = {
                "sub": username,
                "user_id": user_id,
                "tz": tz,
            }
    access_token = await create_access_token(db=db, data=data)
    token_obj = await check_user_token(db=db, user_id=user_id)
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
        result = await db.execute(statement=query)
        return result.scalar()
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def create_user(db: AsyncSession, username, password, tz):
    hashed_password = get_password_hash(password)
    query = insert(Users).values(
        username=username,
        hashed_password=hashed_password,
        role='users',
        is_active=True,
    ).returning(Users.id, Users.username)
    record = await db.execute(query)
    await db.commit()
    user_id = record.scalar()
    token = await create_user_token(db=db, user_id=user_id, username=username, tz=tz)
    user = await get_user_by_name(db=db, username=username)
    print(token)
    print(user)
    if not token:
        return False
    else:
        # token_dict = {"token": token["access_token"], "expires": token["expires"]}
        return {"id": user.id, "name": user.username, "is_active": True, "token": token}
