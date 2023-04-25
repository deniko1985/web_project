from utils import users as users_utils
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from config import SECRET_KEY, ALGORITHM, pwd_context
from schemas.users import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# async def get_current_user(token: str = Depends(oauth2_scheme)):
#    print('token: ', token)
#    user = await users_utils.get_user_by_token(token)
#    print('user: ', user)
#    if not user:
#        raise HTTPException(
#            status_code=status.HTTP_401_UNAUTHORIZED,
#            detail="Invalid authentication credentials",
#            headers={"WWW-Authenticate": "Bearer"},
#        )
#    if not user["is_active"]:
#        raise HTTPException(
#            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
#        )
#    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        # headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
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
                detail="Could not validate credentials",
            )