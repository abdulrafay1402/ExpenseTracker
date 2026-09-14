import shutil
import os
from config import DB_PATH


BACKUP_PATH = os.path.join(os.path.dirname(DB_PATH), "expensemate_backup.db")


def create_backup():
    """Create a file copy of the current database. Returns the backup path."""
    shutil.copy2(DB_PATH, BACKUP_PATH)
    return BACKUP_PATH


def get_backup_path():
    """Return the backup file path if it exists, else None."""
    if os.path.exists(BACKUP_PATH):
        return BACKUP_PATH
    return None


def restore_from_backup(source_path):
    """Overwrite the live database with the provided backup file."""
    shutil.copy2(source_path, DB_PATH)
    return True
