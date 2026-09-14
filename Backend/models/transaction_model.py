from models.database import get_connection
from datetime import datetime


def add_transaction(user_id, type, category_id, amount, currency, rate_to_base,
                    date, description, payment_method_id):
    """Insert a new transaction and return it."""
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO transactions
           (user_id, type, category_id, amount, currency, rate_to_base,
            date, description, payment_method_id, created_at, voided)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
        (user_id, type, category_id, amount, currency, rate_to_base,
         date, description, payment_method_id, datetime.now().isoformat())
    )
    tx_id = cursor.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,)).fetchone()
    conn.close()
    return dict(row)


def get_transactions(user_id, type=None, category_id=None, start_date=None,
                     end_date=None, search=None):
    """List non-voided transactions with optional filters."""
    conn = get_connection()
    query = "SELECT * FROM transactions WHERE user_id = ? AND voided = 0"
    params = [user_id]

    if type:
        query += " AND type = ?"
        params.append(type)
    if category_id:
        query += " AND category_id = ?"
        params.append(category_id)
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    if search:
        query += " AND description LIKE ?"
        params.append(f"%{search}%")

    query += " ORDER BY date DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_transaction_by_id(user_id, transaction_id):
    """Fetch a single transaction."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_transaction(user_id, transaction_id, **fields):
    """Update allowed fields on a transaction."""
    allowed = {"type", "category_id", "amount", "currency", "rate_to_base",
               "date", "description", "payment_method_id"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
        return get_transaction_by_id(user_id, transaction_id)

    conn = get_connection()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [transaction_id, user_id]
    conn.execute(
        f"UPDATE transactions SET {set_clause} WHERE id = ? AND user_id = ?",
        values
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def void_transaction(user_id, transaction_id):
    """Soft-delete a transaction by setting voided=1."""
    conn = get_connection()
    conn.execute(
        "UPDATE transactions SET voided = 1 WHERE id = ? AND user_id = ?",
        (transaction_id, user_id)
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_sum_by_category_and_month(user_id, category_id, month, year):
    """Sum of non-voided expenses for a given category in a given month."""
    conn = get_connection()
    row = conn.execute(
        """SELECT COALESCE(SUM(amount * rate_to_base), 0) as total
           FROM transactions
           WHERE user_id = ? AND category_id = ? AND type = 'expense'
             AND voided = 0
             AND CAST(strftime('%m', date) AS INTEGER) = ?
             AND CAST(strftime('%Y', date) AS INTEGER) = ?""",
        (user_id, category_id, month, year)
    ).fetchone()
    conn.close()
    return row["total"] if row else 0.0


def get_dashboard_totals(user_id, month, year):
    """Return total income, total expenses, and transaction count for the month."""
    conn = get_connection()
    income_row = conn.execute(
        """SELECT COALESCE(SUM(amount * rate_to_base), 0) as total
           FROM transactions
           WHERE user_id = ? AND type = 'income' AND voided = 0
             AND CAST(strftime('%m', date) AS INTEGER) = ?
             AND CAST(strftime('%Y', date) AS INTEGER) = ?""",
        (user_id, month, year)
    ).fetchone()

    expense_row = conn.execute(
        """SELECT COALESCE(SUM(amount * rate_to_base), 0) as total
           FROM transactions
           WHERE user_id = ? AND type = 'expense' AND voided = 0
             AND CAST(strftime('%m', date) AS INTEGER) = ?
             AND CAST(strftime('%Y', date) AS INTEGER) = ?""",
        (user_id, month, year)
    ).fetchone()

    count_row = conn.execute(
        """SELECT COUNT(*) as cnt FROM transactions
           WHERE user_id = ? AND voided = 0
             AND CAST(strftime('%m', date) AS INTEGER) = ?
             AND CAST(strftime('%Y', date) AS INTEGER) = ?""",
        (user_id, month, year)
    ).fetchone()

    conn.close()
    return {
        "total_income": income_row["total"],
        "total_expenses": expense_row["total"],
        "transaction_count": count_row["cnt"]
    }


def get_category_wise_spending(user_id, month, year):
    """Return spending grouped by category for the given month."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT c.name as category_name, c.id as category_id,
                  COALESCE(SUM(t.amount * t.rate_to_base), 0) as total
           FROM transactions t
           JOIN categories c ON t.category_id = c.id
           WHERE t.user_id = ? AND t.type = 'expense' AND t.voided = 0
             AND CAST(strftime('%m', t.date) AS INTEGER) = ?
             AND CAST(strftime('%Y', t.date) AS INTEGER) = ?
           GROUP BY c.id
           ORDER BY total DESC""",
        (user_id, month, year)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_monthly_trend(user_id, year):
    """Return monthly totals for income and expenses for a given year."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT CAST(strftime('%m', date) AS INTEGER) as month,
                  type,
                  COALESCE(SUM(amount * rate_to_base), 0) as total
           FROM transactions
           WHERE user_id = ? AND voided = 0
             AND CAST(strftime('%Y', date) AS INTEGER) = ?
           GROUP BY month, type
           ORDER BY month""",
        (user_id, year)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_income_vs_expense(user_id, year):
    """Return monthly income vs expense comparison for a given year."""
    return get_monthly_trend(user_id, year)
