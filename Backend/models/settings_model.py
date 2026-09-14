from models.database import get_connection


def get_setting(user_id, key):
    """Fetch a setting value by key."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM settings WHERE user_id = ? AND key = ?",
        (user_id, key)
    ).fetchone()
    conn.close()
    return row["value"] if row else None


def set_setting(user_id, key, value):
    """Insert or update a setting."""
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM settings WHERE user_id = ? AND key = ?",
        (user_id, key)
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE settings SET value = ? WHERE user_id = ? AND key = ?",
            (value, user_id, key)
        )
    else:
        conn.execute(
            "INSERT INTO settings (user_id, key, value) VALUES (?, ?, ?)",
            (user_id, key, value)
        )
    conn.commit()
    conn.close()


def get_all_settings(user_id):
    """Return all settings as a dict."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM settings WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}
