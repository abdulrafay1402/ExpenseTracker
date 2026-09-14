from models import transaction_model, category_model
from controllers.transaction_controller import add_transaction
from utils.csv_handler import parse_csv, build_csv
from utils.validators import validate_date
from schemas.transaction_schema import TransactionCreate


async def import_csv(user_id, file_bytes):
    """Parse CSV, validate each row, bulk import valid rows."""
    rows = parse_csv(file_bytes)
    imported = 0
    failed = []

    for idx, row in enumerate(rows, start=2):  # row 1 is header
        try:
            # Validate required fields
            tx_type = row.get("type", "").lower()
            if tx_type not in ("income", "expense"):
                failed.append({"row": idx, "reason": "Invalid or missing type"})
                continue

            category_id = row.get("category_id")
            if not category_id:
                failed.append({"row": idx, "reason": "Missing category_id"})
                continue
            try:
                category_id = int(category_id)
            except (ValueError, TypeError):
                failed.append({"row": idx, "reason": "Invalid category_id"})
                continue

            amount = row.get("amount")
            if not amount:
                failed.append({"row": idx, "reason": "Missing amount"})
                continue
            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                failed.append({"row": idx, "reason": "Invalid amount"})
                continue

            date = row.get("date", "")
            if not validate_date(date):
                failed.append({"row": idx, "reason": "Invalid date format"})
                continue

            currency = row.get("currency", "PKR").upper()

            tx_data = TransactionCreate(
                type=tx_type,
                category_id=category_id,
                amount=amount,
                currency=currency,
                date=date,
                description=row.get("description"),
                payment_method_id=int(row["payment_method_id"]) if row.get("payment_method_id") else None
            )
            await add_transaction(user_id, tx_data)
            imported += 1
        except Exception as e:
            failed.append({"row": idx, "reason": str(e)})

    return {"imported": imported, "failed": failed}


def export_csv(user_id):
    """Export all non-voided transactions as CSV string."""
    transactions = transaction_model.get_transactions(user_id)
    categories = category_model.get_categories(user_id)
    cat_map = {c["id"]: c["name"] for c in categories}
    return build_csv(transactions, cat_map)
