from models import transaction_model, category_model
from controllers.transaction_controller import add_transaction
from utils.csv_handler import parse_csv, build_csv, get_expected_columns
from utils.validators import validate_date
from schemas.transaction_schema import TransactionCreate


def _resolve_category(row, tx_type, categories):
    """Resolve category from name or ID. Returns (category_id, error_msg)."""
    # Build lookup maps
    name_to_id = {}
    id_set = set()
    for c in categories:
        name_to_id[c["name"].lower()] = c["id"]
        id_set.add(c["id"])

    # Try category name first (from 'category' column)
    cat_name = row.get("category", "").strip()
    cat_id_raw = row.get("category_id", "").strip()

    if cat_name:
        # Case-insensitive match by name
        matched_id = name_to_id.get(cat_name.lower())
        if matched_id is not None:
            # Verify type matches
            matched_cat = next((c for c in categories if c["id"] == matched_id), None)
            if matched_cat and matched_cat["type"] != tx_type:
                return None, f"Category '{cat_name}' is type '{matched_cat['type']}', not '{tx_type}'"
            return matched_id, None
        # Name provided but not found — fall through to ID

    if cat_id_raw:
        try:
            cat_id = int(cat_id_raw)
        except (ValueError, TypeError):
            return None, f"Invalid category_id '{cat_id_raw}'"
        if cat_id in id_set:
            matched_cat = next((c for c in categories if c["id"] == cat_id), None)
            if matched_cat and matched_cat["type"] != tx_type:
                return None, f"Category ID {cat_id} is type '{matched_cat['type']}', not '{tx_type}'"
            return cat_id, None
        return None, f"Category ID {cat_id} not found"

    return None, "Missing category (provide 'category' name or 'category_id')"


def _validate_row(idx, row, categories):
    """Validate a single CSV row. Returns (parsed_data, error_msg)."""
    # Type
    tx_type = row.get("type", "").strip().lower()
    if tx_type not in ("income", "expense"):
        return None, "Invalid or missing 'type' (must be 'income' or 'expense')"

    # Category
    cat_id, cat_err = _resolve_category(row, tx_type, categories)
    if cat_err:
        return None, cat_err

    # Amount
    amount_raw = row.get("amount", "").strip()
    if not amount_raw:
        return None, "Missing 'amount'"
    try:
        amount = float(amount_raw)
        if amount <= 0:
            raise ValueError("must be positive")
    except (ValueError, TypeError):
        return None, f"Invalid amount '{amount_raw}'"

    # Date
    date = row.get("date", "").strip()
    if not validate_date(date):
        return None, f"Invalid date '{date}' (expected YYYY-MM-DD)"

    # Currency
    currency = row.get("currency", "PKR").strip().upper() or "PKR"

    # Description
    description = row.get("description", "").strip() or None

    return {
        "type": tx_type,
        "category_id": cat_id,
        "amount": amount,
        "currency": currency,
        "date": date,
        "description": description,
    }, None


def analyze_csv(user_id, file_bytes):
    """Analyze CSV without importing — returns structure info and preview."""
    rows = parse_csv(file_bytes)
    categories = category_model.get_categories(user_id)

    # Column analysis
    if not rows:
        return {
            "total_rows": 0,
            "columns_found": [],
            "columns_missing": list(get_expected_columns().keys()),
            "valid_rows": 0,
            "invalid_rows": 0,
            "preview": [],
            "categories_available": [{"id": c["id"], "name": c["name"], "type": c["type"]} for c in categories],
        }

    actual_columns = list(rows[0].keys())
    expected_columns = list(get_expected_columns().keys())
    columns_missing = [c for c in expected_columns if c not in actual_columns]

    # Validate each row
    valid_rows = []
    invalid_rows = []
    for idx, row in enumerate(rows, start=2):
        parsed, err = _validate_row(idx, row, categories)
        if err:
            invalid_rows.append({"row": idx, "reason": err})
        else:
            valid_rows.append({"row": idx, **parsed})

    # Preview: first 5 valid rows
    preview = valid_rows[:5]

    return {
        "total_rows": len(rows),
        "columns_found": actual_columns,
        "columns_missing": columns_missing,
        "valid_rows": len(valid_rows),
        "invalid_rows": len(invalid_rows),
        "preview": preview,
        "errors": invalid_rows[:10],  # first 10 errors
        "categories_available": [{"id": c["id"], "name": c["name"], "type": c["type"]} for c in categories],
    }


async def import_csv(user_id, file_bytes):
    """Parse CSV, validate each row, import valid rows."""
    rows = parse_csv(file_bytes)
    categories = category_model.get_categories(user_id)
    imported = 0
    failed = []

    for idx, row in enumerate(rows, start=2):
        parsed, err = _validate_row(idx, row, categories)
        if err:
            failed.append({"row": idx, "reason": err})
            continue

        try:
            tx_data = TransactionCreate(
                type=parsed["type"],
                category_id=parsed["category_id"],
                amount=parsed["amount"],
                currency=parsed["currency"],
                date=parsed["date"],
                description=parsed["description"],
            )
            await add_transaction(user_id, tx_data)
            imported += 1
        except Exception as e:
            failed.append({"row": idx, "reason": str(e)})

    return {"imported": imported, "failed": failed, "total_rows": len(rows)}


def export_csv(user_id):
    """Export all non-voided transactions as CSV string."""
    transactions = transaction_model.get_transactions(user_id)
    categories = category_model.get_categories(user_id)
    cat_map = {c["id"]: c["name"] for c in categories}
    return build_csv(transactions, cat_map)
