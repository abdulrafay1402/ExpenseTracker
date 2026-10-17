from services import budget_service


def set_budget(user_id, budget):
    return budget_service.set_budget(
        user_id,
        budget.category_id,
        budget.amount,
        budget.month,
        budget.year,
        budget.alert_threshold,
    )


def list_budgets(user_id, month=None, year=None):
    return budget_service.list_budgets(user_id, month=month, year=year)


def update_budget(user_id, budget_id, budget):
    return budget_service.update_budget(
        user_id,
        budget_id,
        amount=budget.amount,
        alert_threshold=budget.alert_threshold,
    )


def check_alert(user_id, category_id, month=None, year=None):
    return budget_service.check_alert(
        user_id, category_id, month=month, year=year
    )


def check_all_alerts(user_id, month=None, year=None):
    return budget_service.check_all_alerts(user_id, month=month, year=year)
