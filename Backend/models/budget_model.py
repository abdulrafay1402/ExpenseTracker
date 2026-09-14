from models.database import get_connection


def set_budget(user_id, category_id, amount, month, year, alert_threshold=80):
    """Create a new budget entry."""
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO budgets (user_id, category_id, amount, month, year, alert_threshold)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, category_id, amount, month, year, alert_threshold)
    )
    budget_id = cursor.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM budgets WHERE id = ?", (budget_id,)).fetchone()
    conn.close()
    return dict(row)


def get_budgets(user_id, month=None, year=None):
    """List budgets for a user, optionally filtered by month/year."""
    conn = get_connection()
    query = "SELECT * FROM budgets WHERE user_id = ?"
    params = [user_id]
    if month is not None:
        query += " AND month = ?"
        params.append(month)
    if year is not None:
        query += " AND year = ?"
        params.append(year)
    query += " ORDER BY category_id"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_budget_by_id(user_id, budget_id):
    """Fetch a single budget."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM budgets WHERE id = ? AND user_id = ?",
        (budget_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_budget_by_category(user_id, category_id, month, year):
    """Fetch budget for a specific category and month."""
    conn = get_connection()
    row = conn.execute(
        """SELECT * FROM budgets
           WHERE user_id = ? AND category_id = ? AND month = ? AND year = ?""",
        (user_id, category_id, month, year)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_budget(user_id, budget_id, amount=None, alert_threshold=None):
    """Update budget amount and/or alert threshold."""
    conn = get_connection()
    updates = []
    params = []
    if amount is not None:
        updates.append("amount = ?")
        params.append(amount)
    if alert_threshold is not None:
        updates.append("alert_threshold = ?")
        params.append(alert_threshold)

    if updates:
        params.extend([budget_id, user_id])
        conn.execute(
            f"UPDATE budgets SET {', '.join(updates)} WHERE id = ? AND user_id = ?",
            params
        )
        conn.commit()

    row = conn.execute(
        "SELECT * FROM budgets WHERE id = ? AND user_id = ?",
        (budget_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None
