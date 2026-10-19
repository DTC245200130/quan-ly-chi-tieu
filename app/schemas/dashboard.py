from datetime import date
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class DashboardSummary(BaseModel):
    income: Decimal = Decimal(0)
    expense: Decimal = Decimal(0)
    net: Decimal = Decimal(0)
    available_balance: Decimal = Decimal(0)


class DashboardCategorySpending(BaseModel):
    category_id: str
    category_name: str
    color: str
    icon: str
    amount: Decimal
    percentage: float


class DashboardTrendPoint(BaseModel):
    month: int
    year: int
    income: Decimal = Decimal(0)
    expense: Decimal = Decimal(0)


class DashboardBudget(BaseModel):
    id: str
    category_id: str
    category_name: str
    color: str
    icon: str
    limit_amount: Decimal
    spent: Decimal = Decimal(0)
    remaining: Decimal = Decimal(0)
    usage_percentage: float = 0
    is_over: bool = False
    status: Literal["safe", "warning", "over"]


class DashboardGoal(BaseModel):
    id: str
    name: str
    target_amount: Decimal
    current_amount: Decimal = Decimal(0)
    progress_percentage: float = 0
    deadline: Optional[date] = None
    status: str


class DashboardRecentTransaction(BaseModel):
    id: str
    category_id: str
    category_name: str
    category_color: str
    category_icon: str
    amount: Decimal
    type: str
    txn_date: date
    note: Optional[str] = None


class DashboardOut(BaseModel):
    month: int
    year: int
    summary: DashboardSummary
    spending_by_category: list[DashboardCategorySpending] = Field(default_factory=list)
    trend: list[DashboardTrendPoint] = Field(default_factory=list)
    budgets: list[DashboardBudget] = Field(default_factory=list)
    goals: list[DashboardGoal] = Field(default_factory=list)
    recent_transactions: list[DashboardRecentTransaction] = Field(default_factory=list)
