from fastapi import APIRouter, UploadFile, File
from controllers import backup_controller

router = APIRouter(prefix="/backup", tags=["Backup"])


@router.post("")
def create_backup():
    return backup_controller.create_backup()


@router.post("/restore")
async def restore_backup(file: UploadFile | None = File(None)):
    if file is None:
        return backup_controller.restore_latest_backup()
    return await backup_controller.restore_backup(file)
