from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from config import LOCAL_USER_ID
from controllers import csv_controller
import io

router = APIRouter(prefix="/csv", tags=["CSV Import/Export"])


@router.post("/import")
async def import_csv(file: UploadFile = File(...)):
    file_bytes = await file.read()
    return await csv_controller.import_csv(LOCAL_USER_ID, file_bytes)


@router.get("/export")
def export_csv():
    csv_content = csv_controller.export_csv(LOCAL_USER_ID)
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions_export.csv"}
    )
