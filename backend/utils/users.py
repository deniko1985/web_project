import os
from sqlalchemy import and_
from datetime import datetime, timedelta
from jose import jwt


from models.users import users_table as users, tokens
from models.db import database
from config import pwd_context

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username):
    query = (
            users.select()
            .where(users.c.username == username)
            )
    return await database.fetch_one(query)


async def get_user_by_id(user_id: int):
    query = (
            users.select()
            .where(users.c.id == user_id)
            .where(users.c.is_active == True)
            )
    return await database.fetch_one(query)


async def get_user_by_name(username: str):
    query = (
            users.select()
            .where(users.c.username == username)
            .where(users.c.is_active == True)
            )
    return await database.fetch_one(query)


async def check_user_token(user_id: int):
    try:
        query = tokens.select().where(tokens.c.user_id == user_id)
        return await database.fetch_one(query)
    except Exception:
        return None


async def get_user_by_token(token: str):
    try:
        query = tokens.join(users).select().where(
            and_(
                tokens.c.access_token == token,
                tokens.c.expires > datetime.now()
            )
        )
        return await database.fetch_one(query)
    except Exception:
        return None


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
    if token_obj:
        token = token_obj.access_token
        token_id = token_obj.id
        if token and token_id:
            query = (
                tokens.update()
                .where(tokens.c.id == token_id)
                .values(
                    id=token_id,
                    access_token=access_token,
                    expires=datetime.utcnow() + timedelta(weeks=2),
                    user_id=user_id,
                )
                .returning(tokens.c.access_token, tokens.c.expires)
            )
        else:
            query = (
                tokens.insert()
                .values(
                    access_token=access_token,
                    expires=datetime.utcnow() + timedelta(weeks=2),
                    user_id=user_id,
                )
                .returning(tokens.c.access_token, tokens.c.expires)
            )
    else:
        query = (
            tokens.insert()
            .values(
                access_token=access_token,
                expires=datetime.utcnow() + timedelta(weeks=2),
                user_id=user_id,
            )
            .returning(tokens.c.access_token, tokens.c.expires)
        )
    return await database.fetch_one(query)


async def create_user(username, password, tz):
    hashed_password = get_password_hash(password)
    query = users.insert().values(
        username=username,
        hashed_password=hashed_password,
        is_active=True,
        auth_token='',
        )
    user_id = await database.execute(query)
    token = await create_user_token(user_id, username, tz)
    user = await get_user_by_name(username)
    if not token:
        return False
    else:
        token_dict = {"token": token["access_token"], "expires": token["expires"]}
        return {"id": user.id, "name": user.username, "is_active": True, "token": token_dict}
