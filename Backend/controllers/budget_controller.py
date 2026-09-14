from datetime import datetime
from models import budget_model, transaction_model, category_model
from utils.exceptions import ValidationError, NotFoundError


def set_budget(user_id, category_id, amount, month, year, alert_threshold=80):
    """Set a monthly budget for a category."""
    # Check if budget already exists for this category/month
    existing = budget_model.get_budget_by_category(user_id, category_id, month, year)
    if existing:
        raise ValidationError(
            f"Budget already exists for category {category_id} in {month}/{year}. "
            "Use update instead."
        )
    # Validate category exists
    if not category_model.get_category_by_id(user_id, category_id):
        raise NotFoundError(f"Category {category_id} not found.")

    return budget_model.set_budget(user_id, category_id, amount, month, year, alert_threshold)


def list_budgets(user_id, month=None, year=None):
    """List budgets with optional month/year filter."""
    return budget_model.get_budgets(user_id, month=month, year=year)


def update_budget(user_id, budget_id, amount=None, alert_threshold=None):
    """Update a budget's amount or alert threshold."""
    existing = budget_model.get_budget_by_id(user_id, budget_id)
    if not existing:
        raise NotFoundError(f"Budget {budget_id} not found.")
    return budget_model.update_budget(user_id, budget_id, amount=amount,
                                      alert_threshold=alert_threshold)


def check_alert(user_id, category_id, month=None, year=None):
    """Check budget alert status for a single category."""
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year

    budget = budget_model.get_budget_by_category(user_id, category_id, month, year)
    if not budget:
        raise NotFoundError(f"No budget set for category {category_id} in {month}/{year}.")

    spent = transaction_model.get_sum_by_category_and_month(
        user_id, category_id, month, year
    )
    pct = (spent / budget["amount"]) * 100 if budget["amount"] > 0 else 0

    if pct >= 100:
        status = "exceeded"
    elif pct >= budget["alert_threshold"]:
        status = "warning"
    else:
        status = "normal"

    cat = category_model.get_category_by_id(user_id, category_id)
    return {
        "category_id": category_id,
        "category_name": cat["name"] if cat else "Unknown",
        "budget_limit": budget["amount"],
        "spent": spent,
        "percentage": round(pct, 2),
        "status": status
    }


def check_all_alerts(user_id, month=None, year=None):
    """Check alert status for all budgeted categories in the given month."""
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year

    budgets = budget_model.get_budgets(user_id, month=month, year=year)
    alerts = []
    for b in budgets:
        spent = transaction_model.get_sum_by_category_and_month(
            user_id, b["category_id"], month, year
        )
        pct = (spent / b["amount"]) * 100 if b["amount"] > 0 else 0

        if pct >= 100:
            status = "exceeded"
        elif pct >= b["alert_threshold"]:
            status = "warning"
        else:
            status = "normal"

        cat = category_model.get_category_by_id(user_id, b["category_id"])
        alerts.append({
            "category_id": b["category_id"],
            "category_name": cat["name"] if cat else "Unknown",
            "budget_limit": b["amount"],
            "spent": spent,
            "percentage": round(pct, 2),
            "status": status
        })
    return alerts
