from models.database import get_connection


def get_user(user_id):
    """Fetch a single user by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_user(user_id, name, email):
    """Insert a new user and return it."""
    from datetime import datetime
    conn = get_connection()
    conn.execute(
        "INSERT INTO users (id, name, email, created_at) VALUES (?, ?, ?, ?)",
        (user_id, name, email, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return get_user(user_id)
