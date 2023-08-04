from datetime import datetime
import pytz
from sqlalchemy import select, insert
from sqlalchemy.exc import SQLAlchemyError
import logging

from models.budget import Budget
from models.databases import database
from schemas.budget import BudgetSum


# получение пользовательского логгера и установка уровня логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# настройка обработчика и форматировщика в соответствии с нашими нуждами
handler = logging.FileHandler(f"logs/{__name__}.log", mode='w')
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
handler.setFormatter(formatter)
# добавление обработчика к логгеру
logger.addHandler(handler)

logger.info(f"Testing the custom logger for module {__name__}...")


async def get_budget_expense(user_id, date_from=None, date_to=None, full_date=None):
    try:
        if not date_from:
            date_from = datetime.now().replace(day=1)
        else:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
        if not date_to:
            date_to = datetime.now()
        else:
            date_to += ' ' + '23:59:59'
            date_to = datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S')
        query = select(Budget).where(Budget.user_id == user_id)
        if full_date:
            query = query
        else:
            query = query.where(Budget.date <= date_to).where(Budget.date >= date_from)
        records = await database.fetch_all(query)
        expenses_sum = 0
        income_sum = 0
        for record in records:
            data = BudgetSum(**record)
            income_sum += data.income
            expenses_sum += data.expense
        b_sum = {"income_sum": income_sum, "expenses_sum": expenses_sum}
        return b_sum
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def add_budget(user_id, username, income, expense, comment):
    try:
        query = insert(Budget).values(
            user_id=user_id,
            username=username,
            income=float(income),
            expense=float(expense),
            comment=comment,
            date=datetime.now()
        )
        return await database.execute(query)
    except SQLAlchemyError as error:
        logging.error("SQLAlchemyError", exc_info=True)
        return {"error": str(error)}


async def get_date_local(tz, date_from=None, date_to=None):
    if not date_from:
        date_from = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    if not date_to:
        date_to = datetime.now().astimezone(pytz.timezone(tz)).strftime("%Y-%m-%d")
    user_date = {"date_to": date_to, "date_from": date_from}
    return user_date
