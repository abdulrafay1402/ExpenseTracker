import sqlite3
from config import DB_PATH, LOCAL_USER_ID
from datetime import datetime


def get_connection():
    """Return a new connection with row_factory enabled for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    """Create all tables if they don't exist and seed default data."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            name TEXT,
            type TEXT CHECK(type IN ('income','expense')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS payment_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            name TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            type TEXT CHECK(type IN ('income','expense')),
            category_id INTEGER,
            amount REAL,
            currency TEXT DEFAULT 'PKR',
            rate_to_base REAL DEFAULT 1.0,
            date TEXT,
            description TEXT,
            payment_method_id INTEGER,
            created_at TEXT,
            voided INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id)
        );

        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            category_id INTEGER,
            amount REAL,
            month INTEGER,
            year INTEGER,
            alert_threshold REAL DEFAULT 80,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );

        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            key TEXT,
            value TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    # Seed local user if not exists
    cursor.execute("SELECT id FROM users WHERE id = ?", (LOCAL_USER_ID,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (id, name, email, created_at) VALUES (?, ?, ?, ?)",
            (LOCAL_USER_ID, "Local User", "local@expensemate.app", datetime.now().isoformat())
        )

    # Seed default categories if none exist for this user
    cursor.execute("SELECT COUNT(*) as cnt FROM categories WHERE user_id = ?", (LOCAL_USER_ID,))
    if cursor.fetchone()["cnt"] == 0:
        income_categories = ["Salary", "Freelance", "Business", "Gift", "Other"]
        expense_categories = [
            "Food", "Transport", "Bills", "Shopping", "Entertainment",
            "Healthcare", "Education", "Rent", "Subscriptions", "Other"
        ]
        for name in income_categories:
            cursor.execute(
                "INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)",
                (LOCAL_USER_ID, name, "income")
            )
        for name in expense_categories:
            cursor.execute(
                "INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)",
                (LOCAL_USER_ID, name, "expense")
            )

    # Seed default payment methods if none exist for this user
    cursor.execute("SELECT COUNT(*) as cnt FROM payment_methods WHERE user_id = ?", (LOCAL_USER_ID,))
    if cursor.fetchone()["cnt"] == 0:
        methods = ["Cash", "Bank", "Credit Card", "Debit Card", "Digital Wallet", "Other"]
        for name in methods:
            cursor.execute(
                "INSERT INTO payment_methods (user_id, name) VALUES (?, ?)",
                (LOCAL_USER_ID, name)
            )

    conn.commit()
    conn.close()
