from zipfile import BadZipFile

from services import backup_service
from utils.exceptions import ValidationError


def create_backup():
    return backup_service.backup_database()


def restore_latest_backup():
    try:
        return backup_service.restore_latest_backup()
    except (ValueError, BadZipFile) as exc:
        raise ValidationError(f"Invalid backup archive: {exc}") from exc


async def restore_backup(upload):
    try:
        return backup_service.restore_database(
            await upload.read(), upload.filename
        )
    except (ValueError, BadZipFile) as exc:
        raise ValidationError(f"Invalid backup archive: {exc}") from exc
