import os
from dotenv import load_dotenv

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

DB_PATH = os.path.join(BACKEND_DIR, "expense.db")
CURRENCY_API_BASE = "https://open.er-api.com/v6"
LOCAL_USER_ID = "00000000-0000-0000-0000-000000000001"  # placeholder until real auth exists
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DATABASE = os.environ.get("MONGO_DATABASE", "expensemate")
