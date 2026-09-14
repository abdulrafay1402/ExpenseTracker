from pydantic import BaseModel
from typing import Optional, List


class DashboardResponse(BaseModel):
    total_income: float
    total_expenses: float
    remaining: float
    budget_percentage: Optional[float] = None
    top_expense_category: Optional[str] = None
    transaction_count: int


class CategoryWiseItem(BaseModel):
    category_name: str
    category_id: int
    total: float


class CategoryWiseReport(BaseModel):
    month: int
    year: int
    categories: List[CategoryWiseItem]


class MonthlyTrendItem(BaseModel):
    month: int
    type: str
    total: float


class MonthlyTrendReport(BaseModel):
    year: int
    data: List[MonthlyTrendItem]


class IncomeVsExpenseItem(BaseModel):
    month: int
    income: float
    expense: float


class IncomeVsExpenseReport(BaseModel):
    year: int
    data: List[IncomeVsExpenseItem]


class MonthlySummaryResponse(BaseModel):
    month: int
    year: int
    total_income: float
    total_expenses: float
    remaining: float
    transaction_count: int
    top_expense_category: Optional[str] = None
    category_breakdown: List[CategoryWiseItem]
