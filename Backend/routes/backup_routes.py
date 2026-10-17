from fastapi import APIRouter, UploadFile, File
from zipfile import BadZipFile
from services import backup_service
from utils.exceptions import ValidationError

router = APIRouter(prefix="/backup", tags=["Backup"])


@router.post("")
def create_backup():
    return backup_service.backup_database()


@router.post("/restore")
async def restore_backup(file: UploadFile | None = File(None)):
    try:
        if file is None:
            return backup_service.restore_latest_backup()
        return backup_service.restore_database(await file.read(), file.filename)
    except (ValueError, BadZipFile) as exc:
        raise ValidationError(f"Invalid backup archive: {exc}") from exc
