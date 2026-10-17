from fastapi import APIRouter, Query
from typing import Optional
from config import LOCAL_USER_ID
from schemas.budget_schema import BudgetCreate, BudgetUpdate, BudgetResponse, AlertResponse
from services import budget_service

router = APIRouter(prefix="/budget", tags=["Budgets"])


@router.post("", response_model=BudgetResponse)
def set_budget(b: BudgetCreate):
    return budget_service.set_budget(
        LOCAL_USER_ID, b.category_id, b.amount, b.month, b.year, b.alert_threshold
    )


@router.get("", response_model=list[BudgetResponse])
def list_budgets(
    month: Optional[int] = Query(None),
    year: Optional[int] = Query(None)
):
    return budget_service.list_budgets(LOCAL_USER_ID, month=month, year=year)


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(budget_id: int, b: BudgetUpdate):
    return budget_service.update_budget(
        LOCAL_USER_ID, budget_id, amount=b.amount, alert_threshold=b.alert_threshold
    )


@router.get("/alert/{category_id}", response_model=AlertResponse)
def check_alert(
    category_id: int,
    month: Optional[int] = Query(None),
    year: Optional[int] = Query(None)
):
    return budget_service.check_alert(
        LOCAL_USER_ID, category_id, month=month, year=year
    )


@router.get("/alerts", response_model=list[AlertResponse])
def check_all_alerts(
    month: Optional[int] = Query(None),
    year: Optional[int] = Query(None)
):
    return budget_service.check_all_alerts(LOCAL_USER_ID, month=month, year=year)
