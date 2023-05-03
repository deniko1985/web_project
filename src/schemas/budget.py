from pydantic import BaseModel
from pydantic.typing import Optional
from datetime import datetime


class UserBudgetBase(BaseModel):
    id: int
    user_id: int
    username: str
    income: Optional[float]
    expense: Optional[float]
    comment: Optional[str]
    date: datetime


class BudgetSum(BaseModel):
    income: float
    expense: float
