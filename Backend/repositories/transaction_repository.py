import re
from datetime import datetime

from models.database import get_collection, next_id


def add_transaction(
    user_id, type, category_id, amount, currency, rate_to_base,
    date, description, payment_method_id
):
    transaction_id = next_id("transactions")
    transaction = {
        "_id": transaction_id,
        "id": transaction_id,
        "user_id": user_id,
        "type": type,
        "category_id": category_id,
        "amount": amount,
        "currency": currency,
        "rate_to_base": rate_to_base,
        "date": date,
        "description": description,
        "payment_method_id": payment_method_id,
        "created_at": datetime.now().isoformat(),
        "voided": 0,
    }
    get_collection("transactions").insert_one(transaction)
    return transaction


def get_transactions(
    user_id, type=None, category_id=None, start_date=None,
    end_date=None, search=None
):
    query = {"user_id": user_id, "voided": 0}
    if type:
        query["type"] = type
    if category_id is not None:
        query["category_id"] = category_id
    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = start_date
        if end_date:
            query["date"]["$lte"] = end_date
    if search:
        query["description"] = {"$regex": re.escape(search), "$options": "i"}
    return list(
        get_collection("transactions")
        .find(query)
        .sort([("date", -1), ("id", -1)])
    )


def transaction_exists(user_id, type, category_id, amount, date, description):
    query = {
        "user_id": user_id,
        "type": type,
        "category_id": category_id,
        "amount": amount,
        "date": date,
        "voided": 0,
    }
    if description is None:
        query["$or"] = [{"description": None}, {"description": ""}]
    else:
        query["description"] = description
    return get_collection("transactions").count_documents(query, limit=1) > 0


def get_transaction_by_id(user_id, transaction_id):
    return get_collection("transactions").find_one(
        {"id": transaction_id, "user_id": user_id}
    )


def update_transaction(user_id, transaction_id, **fields):
    allowed = {
        "type", "category_id", "amount", "currency", "rate_to_base",
        "date", "description", "payment_method_id",
    }
    updates = {
        key: value for key, value in fields.items()
        if key in allowed and value is not None
    }
    if updates:
        get_collection("transactions").update_one(
            {"id": transaction_id, "user_id": user_id},
            {"$set": updates},
        )
    return get_transaction_by_id(user_id, transaction_id)


def void_transaction(user_id, transaction_id):
    get_collection("transactions").update_one(
        {"id": transaction_id, "user_id": user_id},
        {"$set": {"voided": 1}},
    )
    return get_transaction_by_id(user_id, transaction_id)


def _month_query(year, month=None):
    if month is None:
        return {"date": {"$regex": f"^{year:04d}-"}}
    return {"date": {"$regex": f"^{year:04d}-{month:02d}-"}}


def get_sum_by_category_and_month(user_id, category_id, month, year):
    query = {
        "user_id": user_id,
        "category_id": category_id,
        "type": "expense",
        "voided": 0,
        **_month_query(year, month),
    }
    total = 0.0
    for row in get_collection("transactions").find(query, {"amount": 1, "rate_to_base": 1}):
        total += row.get("amount", 0) * row.get("rate_to_base", 1.0)
    return total


def get_dashboard_totals(user_id, month, year):
    query = {"user_id": user_id, "voided": 0, **_month_query(year, month)}
    totals = {
        "total_income": 0.0,
        "total_expenses": 0.0,
        "transaction_count": 0,
    }
    for row in get_collection("transactions").find(
        query, {"type": 1, "amount": 1, "rate_to_base": 1}
    ):
        totals["transaction_count"] += 1
        key = "total_income" if row["type"] == "income" else "total_expenses"
        totals[key] += row.get("amount", 0) * row.get("rate_to_base", 1.0)
    return totals


def get_category_wise_spending(user_id, month, year):
    transaction_query = {
        "user_id": user_id,
        "type": "expense",
        "voided": 0,
        **_month_query(year, month),
    }
    totals = {}
    for transaction in get_collection("transactions").find(transaction_query):
        category_id = transaction.get("category_id")
        if category_id is None:
            continue
        totals[category_id] = totals.get(category_id, 0.0) + (
            transaction.get("amount", 0) * transaction.get("rate_to_base", 1.0)
        )

    categories = {
        category["id"]: category
        for category in get_collection("categories").find(
            {"user_id": user_id, "id": {"$in": list(totals)}}
        )
    }
    rows = [
        {
            "category_name": categories[category_id]["name"],
            "category_id": category_id,
            "total": total,
        }
        for category_id, total in totals.items()
        if category_id in categories
    ]
    return sorted(rows, key=lambda row: row["total"], reverse=True)


def get_monthly_trend(user_id, year):
    query = {
        "user_id": user_id,
        "voided": 0,
        "date": {"$regex": f"^{year:04d}-"},
    }
    totals = {}
    for transaction in get_collection("transactions").find(query):
        try:
            month = int(transaction["date"][5:7])
        except (KeyError, TypeError, ValueError):
            continue
        key = (month, transaction["type"])
        totals[key] = totals.get(key, 0.0) + (
            transaction.get("amount", 0) * transaction.get("rate_to_base", 1.0)
        )
    return [
        {"month": month, "type": type, "total": total}
        for (month, type), total in sorted(totals.items())
    ]


def get_income_vs_expense(user_id, year):
    return get_monthly_trend(user_id, year)
