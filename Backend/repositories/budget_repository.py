from models.database import get_collection, next_id


def set_budget(user_id, category_id, amount, month, year, alert_threshold=80):
    budget_id = next_id("budgets")
    budget = {
        "_id": budget_id,
        "id": budget_id,
        "user_id": user_id,
        "category_id": category_id,
        "amount": amount,
        "month": month,
        "year": year,
        "alert_threshold": alert_threshold,
    }
    get_collection("budgets").insert_one(budget)
    return budget


def get_budgets(user_id, month=None, year=None):
    query = {"user_id": user_id}
    if month is not None:
        query["month"] = month
    if year is not None:
        query["year"] = year
    return list(get_collection("budgets").find(query).sort("category_id", 1))


def get_budget_by_id(user_id, budget_id):
    return get_collection("budgets").find_one(
        {"id": budget_id, "user_id": user_id}
    )


def get_budget_by_category(user_id, category_id, month, year):
    return get_collection("budgets").find_one(
        {
            "user_id": user_id,
            "category_id": category_id,
            "month": month,
            "year": year,
        }
    )


def update_budget(user_id, budget_id, amount=None, alert_threshold=None):
    updates = {}
    if amount is not None:
        updates["amount"] = amount
    if alert_threshold is not None:
        updates["alert_threshold"] = alert_threshold
    if updates:
        get_collection("budgets").update_one(
            {"id": budget_id, "user_id": user_id}, {"$set": updates}
        )
    return get_budget_by_id(user_id, budget_id)
