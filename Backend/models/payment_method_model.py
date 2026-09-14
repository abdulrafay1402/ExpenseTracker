from models.database import get_connection


def get_payment_methods(user_id):
    """List all payment methods for a user."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM payment_methods WHERE user_id = ? ORDER BY id",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_payment_method_by_id(user_id, method_id):
    """Fetch a single payment method."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM payment_methods WHERE id = ? AND user_id = ?",
        (method_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_payment_method(user_id, name):
    """Insert a new payment method and return it."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO payment_methods (user_id, name) VALUES (?, ?)",
        (user_id, name)
    )
    method_id = cursor.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM payment_methods WHERE id = ?", (method_id,)).fetchone()
    conn.close()
    return dict(row)


def delete_payment_method(user_id, method_id):
    """Delete a payment method only if no transactions reference it."""
    conn = get_connection()
    usage = conn.execute(
        "SELECT COUNT(*) as cnt FROM transactions WHERE payment_method_id = ? AND user_id = ?",
        (method_id, user_id)
    ).fetchone()
    if usage["cnt"] > 0:
        conn.close()
        return False
    conn.execute(
        "DELETE FROM payment_methods WHERE id = ? AND user_id = ?",
        (method_id, user_id)
    )
    conn.commit()
    conn.close()
    return True
