from fastapi import APIRouter, HTTPException, Depends, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from jose import jwt
from starlette.templating import Jinja2Templates
import starlette.status as status

from config import SECRET_KEY, ALGORITHM

from schemas.users import TokenBase, User, UserGeneral
from utils import users
from utils.depend import get_user_by_cookie


router = APIRouter()
templates = Jinja2Templates(directory="/app/main")


@router.post("/auth", response_model=TokenBase)
async def auth(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users.get_user(form_data.username)
    if not user:
        return templates.TemplateResponse(
            "/modal_error.html",
            {"request": request, "data": "Пользователя с таким логином не существует"})
    if not users.verify_password(plain_password=form_data.password, hashed_password=user["hashed_password"]):
        return templates.TemplateResponse(
            "/modal_error.html",
            {"request": request, "data": "Некорректный пароль"})
    token = await users.create_user_token(user_id=user.id, username=form_data.username, tz=form_data.client_secret)
    payload_access = jwt.decode(token['access_token'], SECRET_KEY, algorithms=[ALGORITHM])
    exp_access: str = payload_access.get("exp")
    token_dict = (
                    {
                        "access_token": token.access_token,
                        "expires": token.expires,
                        "token_type": "bearer",
                    }
                )
    return RedirectResponse(
        '/users',
        status_code=status.HTTP_302_FOUND,
        headers={"Set-cookie": f'access_token={token_dict["access_token"]}; expires_in={exp_access}; token_type=bearer'}
        )


@router.get('/users')
async def get_users_page(request: Request, current_user: User = Depends(get_user_by_cookie)):
    print(current_user)
    if current_user:
        return templates.TemplateResponse(
            "/users.html",
            {"request": request, "user_id": current_user.id})
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")


@router.post('/add_user', response_model=UserGeneral)
async def add_user(
                request: Request,
                username=Form(),
                password=Form(),
                client_secret=Form()):
    n_user = await users.get_user_by_name(username)
    if n_user:
        return templates.TemplateResponse(
            "/modal_error.html",
            {"request": request, "data": "Пользователь с таким логином существует"})
    data = await users.create_user(name=username, password=password, tz=client_secret)
    if not data:
        raise HTTPException(status_code=400)
    else:
        return RedirectResponse('/auth')


@router.get('/logout')
async def logout_user(request: Request, current_user: User = Depends(get_user_by_cookie)):
    response = templates.TemplateResponse("/index.html", {"request": request})
    response.delete_cookie("access_token")
    print(response)
    return response


@router.get("/user/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_user_by_cookie)):
    return current_user
