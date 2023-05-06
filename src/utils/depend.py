from utils import users as users_utils
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from config import SECRET_KEY, ALGORITHM
from schemas.users import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")


async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    user = await users_utils.get_user_by_name(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_user_by_cookie(access_token: str | None = Cookie(default=None)):
    if access_token:
        user = await get_current_user(access_token)
        return user
    else:
        return None


async def get_timezone_by_cookie(access_token: str | None = Cookie(default=None)):
    if access_token:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        tz: str = payload.get("tz")
        return tz
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials")
