import os
import shutil
import tempfile
from services.backup_service import create_backup, get_backup_path, restore_from_backup
from utils.exceptions import NotFoundError, ValidationError


def backup_database():
    """Create a backup copy of the database."""
    path = create_backup()
    return {"detail": "Backup created successfully.", "path": path}


def restore_database(file_bytes, filename):
    """Restore the database from an uploaded backup file."""
    # Write uploaded file to a temp location, then restore
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"restore_{filename}")
    try:
        with open(temp_path, "wb") as f:
            f.write(file_bytes)
        restore_from_backup(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    return {"detail": "Database restored successfully from backup."}
