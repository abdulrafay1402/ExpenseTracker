from models.database import get_collection, next_id


def get_categories(user_id, type=None):
    query = {"user_id": user_id}
    if type:
        query["type"] = type
    return list(get_collection("categories").find(query).sort("id", 1))


def get_category_by_id(user_id, category_id):
    return get_collection("categories").find_one(
        {"id": category_id, "user_id": user_id}
    )


def add_category(user_id, name, type):
    category_id = next_id("categories")
    category = {
        "_id": category_id,
        "id": category_id,
        "user_id": user_id,
        "name": name,
        "type": type,
    }
    get_collection("categories").insert_one(category)
    return category


def update_category(user_id, category_id, name):
    get_collection("categories").update_one(
        {"id": category_id, "user_id": user_id}, {"$set": {"name": name}}
    )
    return get_category_by_id(user_id, category_id)


def delete_category(user_id, category_id):
    transactions = get_collection("transactions")
    query = {"category_id": category_id, "user_id": user_id}
    if transactions.count_documents({**query, "voided": 0}) > 0:
        return False
    transactions.update_many(
        {**query, "voided": 1}, {"$set": {"category_id": None}}
    )
    get_collection("budgets").delete_many(
        {"category_id": category_id, "user_id": user_id}
    )
    get_collection("categories").delete_one(
        {"id": category_id, "user_id": user_id}
    )
    return True


def category_exists(user_id, category_id, type=None):
    query = {"id": category_id, "user_id": user_id}
    if type:
        query["type"] = type
    return get_collection("categories").count_documents(query, limit=1) > 0


def get_top_expense_category(user_id, month, year):
    from repositories.transaction_repository import get_category_wise_spending

    results = get_category_wise_spending(user_id, month, year)
    return results[0] if results else None
