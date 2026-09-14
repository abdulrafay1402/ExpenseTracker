from models.database import get_connection


def get_categories(user_id, type=None):
    """List categories for a user, optionally filtered by type."""
    conn = get_connection()
    if type:
        rows = conn.execute(
            "SELECT * FROM categories WHERE user_id = ? AND type = ? ORDER BY id",
            (user_id, type)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM categories WHERE user_id = ? ORDER BY id",
            (user_id,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_category_by_id(user_id, category_id):
    """Fetch a single category."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM categories WHERE id = ? AND user_id = ?",
        (category_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_category(user_id, name, type):
    """Insert a new category and return it."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)",
        (user_id, name, type)
    )
    cat_id = cursor.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM categories WHERE id = ?", (cat_id,)).fetchone()
    conn.close()
    return dict(row)


def update_category(user_id, category_id, name):
    """Rename a category."""
    conn = get_connection()
    conn.execute(
        "UPDATE categories SET name = ? WHERE id = ? AND user_id = ?",
        (name, category_id, user_id)
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM categories WHERE id = ? AND user_id = ?",
        (category_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_category(user_id, category_id):
    """Delete a category only if no transactions reference it."""
    conn = get_connection()
    usage = conn.execute(
        "SELECT COUNT(*) as cnt FROM transactions WHERE category_id = ? AND user_id = ?",
        (category_id, user_id)
    ).fetchone()
    if usage["cnt"] > 0:
        conn.close()
        return False
    conn.execute(
        "DELETE FROM categories WHERE id = ? AND user_id = ?",
        (category_id, user_id)
    )
    conn.commit()
    conn.close()
    return True


def category_exists(user_id, category_id, type=None):
    """Check if a category exists for the user, optionally matching type."""
    conn = get_connection()
    if type:
        row = conn.execute(
            "SELECT id FROM categories WHERE id = ? AND user_id = ? AND type = ?",
            (category_id, user_id, type)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT id FROM categories WHERE id = ? AND user_id = ?",
            (category_id, user_id)
        ).fetchone()
    conn.close()
    return row is not None


def get_top_expense_category(user_id, month, year):
    """Return the category with the highest spending in a given month."""
    conn = get_connection()
    row = conn.execute(
        """SELECT c.name as category_name, c.id as category_id,
                  COALESCE(SUM(t.amount * t.rate_to_base), 0) as total
           FROM transactions t
           JOIN categories c ON t.category_id = c.id
           WHERE t.user_id = ? AND t.type = 'expense' AND t.voided = 0
             AND CAST(strftime('%m', t.date) AS INTEGER) = ?
             AND CAST(strftime('%Y', t.date) AS INTEGER) = ?
           GROUP BY c.id
           ORDER BY total DESC
           LIMIT 1""",
        (user_id, month, year)
    ).fetchone()
    conn.close()
    return dict(row) if row else None
