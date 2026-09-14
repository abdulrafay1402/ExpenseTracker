from datetime import datetime


def validate_date(date_str):
    """Validate date string is in YYYY-MM-DD format. Returns True/False."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False
