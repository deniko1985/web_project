import base64
from typing import List
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from config import SECRET_KEY, ALGORITHM


class Settings(BaseModel):
    authjwt_algorithm: str = ALGORITHM
    authjwt_decode_algorithms: List[str] = [ALGORITHM]
    authjwt_token_location: set = {'cookies', 'headers'}
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_cookie_csrf_protect: bool = False
    # authjwt_public_key: str = base64.b64decode(
    #     settings.JWT_PUBLIC_KEY).decode('utf-8')
    authjwt_private_key: str = base64.b64decode(
        SECRET_KEY).decode('utf-8')


@AuthJWT.load_config
def get_config():
    return Settings()
