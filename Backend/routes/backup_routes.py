from fastapi import APIRouter, UploadFile, File
from config import LOCAL_USER_ID
from controllers import backup_controller

router = APIRouter(prefix="/backup", tags=["Backup"])


@router.post("")
def create_backup():
    return backup_controller.backup_database()


@router.post("/restore")
async def restore_backup(file: UploadFile = File(...)):
    file_bytes = await file.read()
    return backup_controller.restore_database(file_bytes, file.filename)
