import os
from fastapi import APIRouter, HTTPException, Depends, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from jose import jwt
from starlette.templating import Jinja2Templates
import starlette.status as status

from schemas.users import TokenBase, User, UserGeneral, UserCreate, UserToken
from db import users
from utils.user_block import UserBlock
from utils.depend import CurrentUser, DBSession

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


router = APIRouter()
templates = Jinja2Templates(directory="/backend/ui")


@router.post("/auth", response_model=None)
async def auth(
        request: Request,
        db: DBSession,
        form_data: OAuth2PasswordRequestForm = Depends(),
        remember_me=Form(default=None)):
    x = 'x-forwarded-for'.encode('utf-8')
    for header in request.headers.raw:
        if header[0] == x:
            print("Find out the forwarded-for ip address")
            forward_ip = header[1].decode('utf-8')
            print("forward_ip: ", forward_ip)
    user = await users.get_user(db=db, username=form_data.username)
    check_user = UserBlock(username=form_data.username)
    if not user:
        return templates.TemplateResponse(
            "/modal_error.html",
            {"request": request, "data": "Пользователя с таким логином не существует"})
    if not users.verify_password(plain_password=form_data.password, hashed_password=user.hashed_password):
        data = await check_user.check_to_db()
        return templates.TemplateResponse(
            "/modal_error.html",
            {"request": request, "data": f"Некорректный пароль, {data['error']}"})
    check_block = await check_user.return_ttl()
    if check_block:
        return templates.TemplateResponse(
            "/modal_error.html",
            {"request": request, "data": f"Вы заблокированы на {check_block} минут"})
    token = await users.create_user_token(
        db=db,
        user_id=user.id,
        username=form_data.username,
        tz=form_data.client_secret
    )
    payload_access = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp_access: str = payload_access.get("exp")
    token_dict = (
                    {
                        "access_token": token,
                    }
                )
    if remember_me:
        return RedirectResponse(
            '/users',
            status_code=status.HTTP_302_FOUND,
            headers=(
                {"Set-cookie": f'access_token={token_dict["access_token"]}; expires_in={exp_access}; token_type=bearer'}
            )
        )
    else:
        return RedirectResponse(
            '/users',
            status_code=status.HTTP_302_FOUND,
            headers={"Set-cookie": f'access_token={token_dict["access_token"]}'})


@router.post("/auth_company", response_model=None)
async def auth_company(request: Request, db: DBSession, form_data: OAuth2PasswordRequestForm = Depends()):
    x = 'x-forwarded-for'.encode('utf-8')
    for header in request.headers.raw:
        if header[0] == x:
            print("Find out the forwarded-for ip address")
            forward_ip = header[1].decode('utf-8')
            print("forward_ip: ", forward_ip)


@router.get('/users')
async def get_users_page(request: Request, db: DBSession, current_user: CurrentUser):
    if current_user:
        return templates.TemplateResponse(
            "/users.html",
            {"request": request, "user_id": current_user.id})
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")


@router.post('/add_user', response_model=None)
async def add_user(
        request: Request,
        db: DBSession,
        username=Form(),
        password=Form(),
        client_secret=Form()):
    n_user = await users.get_user_by_name(db=db, username=username)
    if n_user:
        return templates.TemplateResponse(
            "/modal_error.html",
            {"request": request, "data": "Пользователь с таким логином существует"})
    data = await users.create_user(db=db, username=username, password=password, tz=client_secret)
    print("data: ", data)
    if not data:
        raise HTTPException(status_code=400)
    else:
        return RedirectResponse('/auth')


@router.get('/logout')
async def logout_user(request: Request, db: DBSession, current_user: CurrentUser):
    response = templates.TemplateResponse("/index.html", {"request": request})
    response.delete_cookie("access_token")
    return response


@router.get("/user/me", response_model=User)
async def read_users_me(db: DBSession, current_user: CurrentUser):
    return current_user


@router.post('/add_company')
async def add_company(
        request: Request,
        email=Form(),
        inn=Form(),
        password=Form(),
        client_secret=Form()):
    print(email, inn, password)
