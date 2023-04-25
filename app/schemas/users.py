from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    """ Проверяет sign-up запрос """
    username: str
    password: str


class UserBase(BaseModel):
    """ Формирует тело ответа с деталями пользователя """
    id: int
    user_id: int
    username: str
    hashed_password: str
    is_active: bool
    auth_token: str


class User(BaseModel):
    """ Формирует тело ответа с деталями пользователя и токеном """
    # token: TokenBase = {}
    id: int
    username: str
    hashed_password: str
    is_active: bool
    auth_token: str


class UserGet(BaseModel):
    id: int
    username: str
    hashed_password: str
    email: str
    is_active: bool
    auth_token: str


class UserGeneral(BaseModel):
    id: int
    username: str
    is_active: bool


class Tokens(BaseModel):
    id: int
    access_token: str
    expires: int
    user_id: int


class TokenData(BaseModel):
    username: str | None = None
    password: str | None = None


class TokenBase(BaseModel):
    access_token: str
    expires: datetime
    token_type: Optional[str] = "bearer"

    class Config:
        allow_population_by_field_name = True


class UserToken(UserGet):
    """ Формирует тело ответа с деталями пользователя и токеном """
    access_token: TokenBase = {}
