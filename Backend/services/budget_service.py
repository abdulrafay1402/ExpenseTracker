"""Application rules for monthly budgets and their spending alerts."""

from datetime import datetime

from repositories import (
    budget_repository,
    category_repository,
    transaction_repository,
)
from utils.exceptions import NotFoundError, ValidationError


class BudgetService:
    """Coordinate budget persistence and derive consistent alert results."""

    def __init__(self, budgets, categories, transactions):
        self._budgets = budgets
        self._categories = categories
        self._transactions = transactions

    @staticmethod
    def _period(month, year):
        now = datetime.now()
        return (
            month if month is not None else now.month,
            year if year is not None else now.year,
        )

    @staticmethod
    def _alert(category_id, category, budget, spent):
        limit = budget["amount"]
        percentage = (spent / limit) * 100 if limit > 0 else 0
        if percentage >= 100:
            status = "exceeded"
        elif percentage >= budget["alert_threshold"]:
            status = "warning"
        else:
            status = "normal"
        return {
            "category_id": category_id,
            "category_name": category["name"] if category else "Unknown",
            "budget_limit": limit,
            "spent": spent,
            "percentage": round(percentage, 2),
            "status": status,
        }

    def set_budget(self, user_id, category_id, amount, month, year, alert_threshold=80):
        existing = self._budgets.get_budget_by_category(
            user_id, category_id, month, year
        )
        if existing:
            raise ValidationError(
                f"Budget already exists for category {category_id} in {month}/{year}. "
                "Use update instead."
            )
        if not self._categories.get_category_by_id(user_id, category_id):
            raise NotFoundError(f"Category {category_id} not found.")
        return self._budgets.set_budget(
            user_id, category_id, amount, month, year, alert_threshold
        )

    def list_budgets(self, user_id, month=None, year=None):
        return self._budgets.get_budgets(user_id, month=month, year=year)

    def update_budget(self, user_id, budget_id, amount=None, alert_threshold=None):
        if not self._budgets.get_budget_by_id(user_id, budget_id):
            raise NotFoundError(f"Budget {budget_id} not found.")
        return self._budgets.update_budget(
            user_id, budget_id, amount=amount, alert_threshold=alert_threshold
        )

    def check_alert(self, user_id, category_id, month=None, year=None):
        month, year = self._period(month, year)
        budget = self._budgets.get_budget_by_category(
            user_id, category_id, month, year
        )
        if not budget:
            raise NotFoundError(
                f"No budget set for category {category_id} in {month}/{year}."
            )
        spent = self._transactions.get_sum_by_category_and_month(
            user_id, category_id, month, year
        )
        category = self._categories.get_category_by_id(user_id, category_id)
        return self._alert(category_id, category, budget, spent)

    def check_all_alerts(self, user_id, month=None, year=None):
        month, year = self._period(month, year)
        alerts = []
        for budget in self._budgets.get_budgets(
            user_id, month=month, year=year
        ):
            category_id = budget["category_id"]
            spent = self._transactions.get_sum_by_category_and_month(
                user_id, category_id, month, year
            )
            category = self._categories.get_category_by_id(user_id, category_id)
            alerts.append(self._alert(category_id, category, budget, spent))
        return alerts


_service = BudgetService(
    budget_repository,
    category_repository,
    transaction_repository,
)


def set_budget(user_id, category_id, amount, month, year, alert_threshold=80):
    return _service.set_budget(
        user_id, category_id, amount, month, year, alert_threshold
    )


def list_budgets(user_id, month=None, year=None):
    return _service.list_budgets(user_id, month, year)


def update_budget(user_id, budget_id, amount=None, alert_threshold=None):
    return _service.update_budget(
        user_id, budget_id, amount=amount, alert_threshold=alert_threshold
    )


def check_alert(user_id, category_id, month=None, year=None):
    return _service.check_alert(user_id, category_id, month, year)


def check_all_alerts(user_id, month=None, year=None):
    return _service.check_all_alerts(user_id, month, year)
