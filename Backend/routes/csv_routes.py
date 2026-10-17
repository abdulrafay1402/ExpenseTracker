from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from config import LOCAL_USER_ID
from controllers import csv_controller
import io

router = APIRouter(prefix="/csv", tags=["CSV Import/Export"])


@router.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):
    """Analyze CSV structure without importing — preview and validation only."""
    return await csv_controller.analyze_csv(LOCAL_USER_ID, file)


@router.post("/import")
async def import_csv(file: UploadFile = File(...)):
    return await csv_controller.import_csv(LOCAL_USER_ID, file)


@router.get("/export")
def export_csv():
    csv_content = csv_controller.export_csv(LOCAL_USER_ID)
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions_export.csv"}
    )


@router.get("/guidelines")
def csv_guidelines():
    return csv_controller.csv_guidelines()
