from datetime import datetime
from models import transaction_model, category_model, budget_model
from utils.exceptions import NotFoundError


def get_dashboard(user_id, month=None, year=None):
    """Generate dashboard summary data."""
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year

    totals = transaction_model.get_dashboard_totals(user_id, month, year)
    top_cat = category_model.get_top_expense_category(user_id, month, year)

    # Calculate overall budget percentage
    budgets = budget_model.get_budgets(user_id, month=month, year=year)
    total_budget = sum(b["amount"] for b in budgets)
    budget_pct = None
    if total_budget > 0:
        budget_pct = round((totals["total_expenses"] / total_budget) * 100, 2)

    return {
        "total_income": totals["total_income"],
        "total_expenses": totals["total_expenses"],
        "remaining": totals["total_income"] - totals["total_expenses"],
        "budget_percentage": budget_pct,
        "top_expense_category": top_cat["category_name"] if top_cat else None,
        "transaction_count": totals["transaction_count"]
    }


def category_wise_report(user_id, month=None, year=None):
    """Category-wise spending report."""
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year

    data = transaction_model.get_category_wise_spending(user_id, month, year)
    return {
        "month": month,
        "year": year,
        "categories": data
    }


def monthly_trend(user_id, year=None):
    """Monthly income/expense trend for a given year."""
    if year is None:
        year = datetime.now().year

    data = transaction_model.get_monthly_trend(user_id, year)
    return {
        "year": year,
        "data": data
    }


def income_vs_expense(user_id, year=None):
    """Monthly income vs expense comparison."""
    if year is None:
        year = datetime.now().year

    raw = transaction_model.get_income_vs_expense(user_id, year)

    # Pivot into per-month entries
    monthly = {}
    for entry in raw:
        m = entry["month"]
        if m not in monthly:
            monthly[m] = {"month": m, "income": 0.0, "expense": 0.0}
        if entry["type"] == "income":
            monthly[m]["income"] = entry["total"]
        else:
            monthly[m]["expense"] = entry["total"]

    return {
        "year": year,
        "data": sorted(monthly.values(), key=lambda x: x["month"])
    }


def monthly_summary(user_id, month=None, year=None):
    """Full text-style monthly summary."""
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year

    totals = transaction_model.get_dashboard_totals(user_id, month, year)
    top_cat = category_model.get_top_expense_category(user_id, month, year)
    cat_data = transaction_model.get_category_wise_spending(user_id, month, year)

    return {
        "month": month,
        "year": year,
        "total_income": totals["total_income"],
        "total_expenses": totals["total_expenses"],
        "remaining": totals["total_income"] - totals["total_expenses"],
        "transaction_count": totals["transaction_count"],
        "top_expense_category": top_cat["category_name"] if top_cat else None,
        "category_breakdown": cat_data
    }
