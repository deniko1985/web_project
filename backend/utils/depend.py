import os
from typing import Annotated
from db import users as users_utils
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from models.databases import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.users import UserBase, TokenData

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> UserBase:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        return None
    user = await users_utils.get_user_by_name(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_user_by_cookie(db: AsyncSession = Depends(get_db), access_token: str | None = Cookie(default=None)):
    if access_token:
        return await get_current_user(db=db, token=access_token)
    else:
        return None


async def get_timezone_by_cookie(db: AsyncSession = Depends(get_db), access_token: str | None = Cookie(default=None)):
    if access_token:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("tz")
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials")


DBSession = Annotated[AsyncSession, Depends(get_db)]
# CurrentUser = Annotated[UserBase, Depends(get_current_user)]
CurrentUser = Annotated[UserBase, Depends(get_user_by_cookie)]
