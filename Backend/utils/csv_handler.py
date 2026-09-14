import csv
import io


def parse_csv(file_bytes):
    """Parse uploaded CSV bytes and return a list of row dicts."""
    text = file_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        # Strip whitespace from keys and values
        cleaned = {k.strip(): v.strip() if v else v for k, v in row.items()}
        rows.append(cleaned)
    return rows


def build_csv(transactions, categories_map):
    """Build CSV string from a list of transaction dicts."""
    output = io.StringIO()
    fieldnames = ["type", "category", "category_id", "amount", "currency",
                  "date", "description"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for tx in transactions:
        writer.writerow({
            "type": tx["type"],
            "category": categories_map.get(tx.get("category_id"), "Unknown"),
            "category_id": tx.get("category_id", ""),
            "amount": tx["amount"],
            "currency": tx["currency"],
            "date": tx["date"],
            "description": tx.get("description", ""),
        })
    return output.getvalue()


def get_expected_columns():
    """Return the expected CSV columns with descriptions."""
    return {
        "type": "Required. Must be 'income' or 'expense'.",
        "category": "Optional. Category name (will be matched to existing categories).",
        "category_id": "Optional. Category numeric ID (used if category name not found).",
        "amount": "Required. Positive number (e.g. 1500 or 99.50).",
        "currency": "Optional. Currency code (defaults to PKR). E.g. PKR, USD, EUR.",
        "date": "Required. Format: YYYY-MM-DD (e.g. 2025-01-15).",
        "description": "Optional. Any text description.",
    }
