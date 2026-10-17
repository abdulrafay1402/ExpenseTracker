from models.database import get_collection, next_id


def get_payment_methods(user_id):
    return list(
        get_collection("payment_methods")
        .find({"user_id": user_id})
        .sort("id", 1)
    )


def get_payment_method_by_id(user_id, method_id):
    return get_collection("payment_methods").find_one(
        {"id": method_id, "user_id": user_id}
    )


def add_payment_method(user_id, name):
    method_id = next_id("payment_methods")
    method = {
        "_id": method_id,
        "id": method_id,
        "user_id": user_id,
        "name": name,
    }
    get_collection("payment_methods").insert_one(method)
    return method


def delete_payment_method(user_id, method_id):
    if get_collection("transactions").count_documents(
        {"payment_method_id": method_id, "user_id": user_id}
    ):
        return False
    get_collection("payment_methods").delete_one(
        {"id": method_id, "user_id": user_id}
    )
    return True
