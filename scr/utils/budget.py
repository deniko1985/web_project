from datetime import datetime
import pytz

from models.budget import budget_table as budget
from models.db import database
from schemas.budget import BudgetSum


async def get_budget_expense(user_id, date_from=None, date_to=None, full_date=None):
    if not date_from:
        date_from = datetime.now().replace(day=1)
    else:
        date_from = datetime.strptime(date_from, '%Y-%m-%d')
    if not date_to:
        date_to = datetime.now()
    else:
        date_to += ' ' + '23:59:59'
        date_to = datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')
    query = budget.select().where(budget.c.user_id == user_id)
    if full_date:
        query = query
    else:
        query = query.where(budget.c.date <= date_to).where(budget.c.date >= date_from)
    records = await database.fetch_all(query)
    expenses_sum = 0
    income_sum = 0
    for record in records:
        data = BudgetSum(**record)
        income_sum += data.income
        expenses_sum += data.expense
    b_sum = {"income_sum": income_sum, "expenses_sum": expenses_sum}
    return b_sum


async def add_budget(user_id, username, income, expense, comment):
    query = budget.insert().values(
        user_id=user_id,
        username=username,
        income=float(income),
        expense=float(expense),
        comment=comment,
        date=datetime.now()
        )
    return await database.execute(query)


async def get_date_local(tz, date_from=None, date_to=None):
    if not date_from:
        date_from = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    if not date_to:
        date_to = datetime.now().astimezone(pytz.timezone(tz)).strftime("%Y-%m-%d")
    user_date = {"date_to": date_to, "date_from": date_from}
    return user_date
