from models import transaction_model, category_model
from controllers.transaction_controller import add_transaction
from utils.csv_handler import parse_csv, build_csv, get_expected_columns
from utils.validators import validate_date
from schemas.transaction_schema import TransactionCreate


def _category_type_error(category, tx_type):
    """Return an error message if the category type does not match the
    transaction type, otherwise None (perfective: extracted guard clause)."""
    if category["type"] != tx_type:
        return (f"Category '{category['name']}' is type "
                f"'{category['type']}', not '{tx_type}'")
    return None


def _match_category_name(cat_name, categories):
    """Case-insensitive category name lookup. Returns (category, error_msg)."""
    for c in categories:
        if c["name"].lower() == cat_name.lower():
            return c, None
    return None, None  # not found is not an error — caller may fall back to ID


def _match_category_id(cat_id_raw, categories):
    """Numeric category ID lookup. Returns (category, error_msg)."""
    try:
        cat_id = int(cat_id_raw)
    except (ValueError, TypeError):
        return None, f"Invalid category_id '{cat_id_raw}'"
    for c in categories:
        if c["id"] == cat_id:
            return c, None
    return None, f"Category ID {cat_id} not found"


def _resolve_category(row, tx_type, categories):
    """Resolve category from name or ID. Returns (category_id, error_msg)."""
    cat_name = row.get("category", "").strip()
    cat_id_raw = row.get("category_id", "").strip()

    # Name takes precedence; fall through to ID when the name is unknown.
    category = None
    if cat_name:
        category, _ = _match_category_name(cat_name, categories)
    if category is None and cat_id_raw:
        category, err = _match_category_id(cat_id_raw, categories)
        if err:
            return None, err
    if category is None:
        return None, "Missing category (provide 'category' name or 'category_id')"

    err = _category_type_error(category, tx_type)
    if err:
        return None, err
    return category["id"], None


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
    """Parse CSV, validate each row, import valid rows, skip duplicates."""
    rows = parse_csv(file_bytes)
    categories = category_model.get_categories(user_id)
    imported = 0
    duplicates = 0
    failed = []

    for idx, row in enumerate(rows, start=2):
        parsed, err = _validate_row(idx, row, categories)
        if err:
            failed.append({"row": idx, "reason": err})
            continue

        # Duplicate guard: skip rows identical to one already in the DB
        # (corrective fix — re-importing a file used to duplicate everything).
        if transaction_model.transaction_exists(
            user_id,
            parsed["type"],
            parsed["category_id"],
            parsed["amount"],
            parsed["date"],
            parsed["description"],
        ):
            duplicates += 1
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

    return {"imported": imported, "duplicates": duplicates,
            "failed": failed, "total_rows": len(rows)}


def export_csv(user_id):
    """Export all non-voided transactions as CSV string."""
    transactions = transaction_model.get_transactions(user_id)
    categories = category_model.get_categories(user_id)
    cat_map = {c["id"]: c["name"] for c in categories}
    return build_csv(transactions, cat_map)
