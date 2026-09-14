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
    fieldnames = ["id", "type", "category", "amount", "currency", "date",
                  "description", "payment_method_id"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for tx in transactions:
        writer.writerow({
            "id": tx["id"],
            "type": tx["type"],
            "category": categories_map.get(tx.get("category_id"), "Unknown"),
            "amount": tx["amount"],
            "currency": tx["currency"],
            "date": tx["date"],
            "description": tx.get("description", ""),
            "payment_method_id": tx.get("payment_method_id", ""),
        })
    return output.getvalue()
