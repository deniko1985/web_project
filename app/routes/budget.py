
from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import RedirectResponse
from starlette.templating import Jinja2Templates
import starlette.status as status

from schemas.users import User
from utils import budget
from utils.depend import get_user_by_cookie, get_timezone_by_cookie

router = APIRouter()
templates = Jinja2Templates(directory="/app/main")


@router.get("/budget")
async def get_budget_page(
                        request: Request,
                        current_user: User = Depends(get_user_by_cookie),
                        tz: User = Depends(get_timezone_by_cookie)):
    b_sum = await budget.get_budget_expense(current_user.id)
    date = await budget.get_date_local(tz)
    if current_user:
        return templates.TemplateResponse(
                                        "/budget.html",
                                        {"request": request,
                                         "b_sum": b_sum,
                                         "date": date})
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")


@router.post("/add_budget_data")
async def add_budget_data(
                        request: Request,
                        income=Form(default=None),
                        expense=Form(default=None),
                        comment=Form(default=None),
                        current_user: User = Depends(get_user_by_cookie)):
    user_id = current_user.id
    username = current_user.username
    if not income and not expense:
        return templates.TemplateResponse(
                "/modal_error.html",
                {"request": request, "data": "Нельзя отправлять с пустыми полями дохода и расхода!"})
    if not income:
        income = 0.0
    if not expense:
        expense = 0.0
    response = await budget.add_budget(user_id, username, income, expense, comment)
    if not response:
        return templates.TemplateResponse(
            "/modal_error.html",
            {"request": request, "data": "Ошибка добавления в БД"})
    else:
        return RedirectResponse(
                    '/budget',
                    status_code=status.HTTP_302_FOUND)


@router.post("/get_data_for_period")
async def get_data_for_period(
                            request: Request,
                            date_from=Form(default=None),
                            date_to=Form(default=None),
                            full_date=Form(default=None),
                            current_user: User = Depends(get_user_by_cookie),
                            tz: User = Depends(get_timezone_by_cookie)):
    user_id = current_user.id
    b_sum = await budget.get_budget_expense(user_id, date_from, date_to, full_date)
    date = await budget.get_date_local(tz, date_from, date_to)
    if current_user:
        return templates.TemplateResponse(
                                        "/budget.html",
                                        {"request": request,
                                         "b_sum": b_sum,
                                         "date": date})
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")
