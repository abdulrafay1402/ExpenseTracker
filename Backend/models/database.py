"""MongoDB connection and initialization for ExpenseMate."""

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from config import LOCAL_USER_ID, MONGO_DATABASE, MONGO_URI

_client = None


def get_client():
    """Return the shared MongoDB client, creating it on first use."""
    global _client
    if _client is None:
        if not MONGO_URI:
            raise RuntimeError(
                "MONGO_URI is required. Set it in Backend/.env before starting the API."
            )
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    return _client


def get_database():
    """Return ExpenseMate's configured MongoDB database."""
    return get_client()[MONGO_DATABASE]


def get_collection(name):
    """Return a collection from the configured MongoDB database."""
    return get_database()[name]


def close_client():
    """Close the shared client, primarily for application shutdown and tests."""
    global _client
    if _client is not None:
        _client.close()
        _client = None


def create_tables():
    """Initialize MongoDB indexes, local user, and default reference data."""
    database = get_database()
    try:
        get_client().admin.command("ping")
        database.categories.create_index([("user_id", 1), ("id", 1)])
        database.transactions.create_index(
            [("user_id", 1), ("voided", 1), ("date", -1), ("id", -1)]
        )
        database.budgets.create_index(
            [("user_id", 1), ("category_id", 1), ("month", 1), ("year", 1)]
        )
        database.settings.create_index([("user_id", 1), ("key", 1)], unique=True)

        database.users.update_one(
            {"_id": LOCAL_USER_ID},
            {
                "$setOnInsert": {
                    "id": LOCAL_USER_ID,
                    "name": "Local User",
                    "email": "local@expensemate.app",
                }
            },
            upsert=True,
        )

        if database.categories.count_documents({"user_id": LOCAL_USER_ID}) == 0:
            categories = [
                {"name": name, "type": "income"}
                for name in ["Salary", "Freelance", "Business", "Gift", "Other"]
            ] + [
                {"name": name, "type": "expense"}
                for name in [
                    "Food", "Transport", "Bills", "Shopping", "Entertainment",
                    "Healthcare", "Education", "Rent", "Subscriptions", "Other",
                ]
            ]
            for category in categories:
                category_id = next_id("categories")
                database.categories.insert_one(
                    {
                        "_id": category_id,
                        "id": category_id,
                        "user_id": LOCAL_USER_ID,
                        **category,
                    }
                )

        if database.payment_methods.count_documents({"user_id": LOCAL_USER_ID}) == 0:
            for name in [
                "Cash", "Bank", "Credit Card", "Debit Card", "Digital Wallet", "Other"
            ]:
                method_id = next_id("payment_methods")
                database.payment_methods.insert_one(
                    {
                        "_id": method_id,
                        "id": method_id,
                        "user_id": LOCAL_USER_ID,
                        "name": name,
                    }
                )

        for collection_name in (
            "categories", "payment_methods", "transactions", "budgets", "settings"
        ):
            latest = database[collection_name].find_one(
                {"id": {"$type": "number"}}, sort=[("id", -1)]
            )
            if latest:
                database["_sequences"].update_one(
                    {"_id": collection_name},
                    {"$max": {"value": latest["id"]}},
                    upsert=True,
                )
    except PyMongoError as exc:
        raise RuntimeError(
            f"Could not initialize MongoDB ({type(exc).__name__}); "
            "check Atlas availability and database permissions."
        ) from exc


def next_id(collection_name):
    """Allocate a monotonically increasing integer ID for an existing API."""
    from pymongo import ReturnDocument

    counter = get_collection("_sequences").find_one_and_update(
        {"_id": collection_name},
        {"$inc": {"value": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return counter["value"]
