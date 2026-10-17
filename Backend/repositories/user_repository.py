from datetime import datetime

from models.database import get_collection


def get_user(user_id):
    return get_collection("users").find_one({"id": user_id})


def create_user(user_id, name, email):
    user = {
        "_id": user_id,
        "id": user_id,
        "name": name,
        "email": email,
        "created_at": datetime.now().isoformat(),
    }
    get_collection("users").insert_one(user)
    return user
