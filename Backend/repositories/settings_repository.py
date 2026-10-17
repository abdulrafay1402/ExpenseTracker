from models.database import get_collection, next_id


def get_setting(user_id, key):
    setting = get_collection("settings").find_one(
        {"user_id": user_id, "key": key}
    )
    return setting["value"] if setting else None


def set_setting(user_id, key, value):
    collection = get_collection("settings")
    setting = collection.find_one({"user_id": user_id, "key": key})
    if setting:
        collection.update_one(
            {"_id": setting["_id"]}, {"$set": {"value": value}}
        )
        return
    setting_id = next_id("settings")
    collection.update_one(
        {"user_id": user_id, "key": key},
        {
            "$setOnInsert": {
                "_id": setting_id,
                "id": setting_id,
                "user_id": user_id,
                "key": key,
                "value": value,
            }
        },
        upsert=True,
    )
