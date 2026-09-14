from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from config import LOCAL_USER_ID
from controllers import csv_controller
from utils.csv_handler import get_expected_columns
import io

router = APIRouter(prefix="/csv", tags=["CSV Import/Export"])


@router.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):
    """Analyze CSV structure without importing — preview and validation only."""
    file_bytes = await file.read()
    return csv_controller.analyze_csv(LOCAL_USER_ID, file_bytes)


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


@router.get("/guidelines")
def csv_guidelines():
    """Return CSV format guidelines and available categories."""
    return {
        "columns": get_expected_columns(),
        "date_format": "YYYY-MM-DD (e.g. 2025-01-15)",
        "example_row": "expense,Food,3,1500,PKR,2025-01-15,Lunch at cafe",
    }
