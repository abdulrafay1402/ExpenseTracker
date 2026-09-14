from fastapi import APIRouter, Query
from typing import Optional
from config import LOCAL_USER_ID
from schemas.report_schema import (
    DashboardResponse, CategoryWiseReport, MonthlyTrendReport,
    IncomeVsExpenseReport, MonthlySummaryResponse
)
from controllers import report_controller

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    month: Optional[int] = Query(None),
    year: Optional[int] = Query(None)
):
    return report_controller.get_dashboard(LOCAL_USER_ID, month=month, year=year)


@router.get("/category-wise", response_model=CategoryWiseReport)
def category_wise_report(
    month: Optional[int] = Query(None),
    year: Optional[int] = Query(None)
):
    return report_controller.category_wise_report(LOCAL_USER_ID, month=month, year=year)


@router.get("/monthly", response_model=MonthlyTrendReport)
def monthly_trend(year: Optional[int] = Query(None)):
    return report_controller.monthly_trend(LOCAL_USER_ID, year=year)


@router.get("/income-vs-expense", response_model=IncomeVsExpenseReport)
def income_vs_expense(year: Optional[int] = Query(None)):
    return report_controller.income_vs_expense(LOCAL_USER_ID, year=year)


@router.get("/monthly-summary", response_model=MonthlySummaryResponse)
def monthly_summary(
    month: Optional[int] = Query(None),
    year: Optional[int] = Query(None)
):
    return report_controller.monthly_summary(LOCAL_USER_ID, month=month, year=year)
