from services import csv_service
from utils.csv_handler import get_expected_columns


async def analyze_csv(user_id, upload):
    return csv_service.analyze_csv(user_id, await upload.read())


async def import_csv(user_id, upload):
    return await csv_service.import_csv(user_id, await upload.read())


def export_csv(user_id):
    return csv_service.export_csv(user_id)


def csv_guidelines():
    return {
        "columns": get_expected_columns(),
        "date_format": "YYYY-MM-DD (e.g. 2025-01-15)",
        "example_row": "expense,Food,3,1500,PKR,2025-01-15,Lunch at cafe",
    }
