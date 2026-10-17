"""CSV analysis, validation, import, and export application workflows."""

from fastapi import HTTPException

from repositories import category_repository, transaction_repository
from schemas.transaction_schema import TransactionCreate
from services.transaction_service import add_transaction
from utils.csv_handler import (
    build_csv,
    get_expected_columns,
    parse_csv,
)
from utils.validators import validate_date


class CsvImportExportService:
    """Validate CSV rows once and coordinate preview, import, and export."""

    def __init__(self, categories, transactions, transaction_writer):
        self._categories = categories
        self._transactions = transactions
        self._transaction_writer = transaction_writer

    @staticmethod
    def _category_indexes(categories):
        by_name = {}
        by_id = {}
        for category in categories:
            by_name.setdefault(category["name"].casefold(), category)
            by_id[category["id"]] = category
        return by_name, by_id

    @classmethod
    def _validate_row(cls, row, categories):
        tx_type = row.get("type", "").strip().lower()
        if tx_type not in {"income", "expense"}:
            return None, "Invalid or missing 'type' (must be 'income' or 'expense')"

        by_name, by_id = cls._category_indexes(categories)
        category_name = row.get("category", "").strip()
        category_id_raw = row.get("category_id", "").strip()
        category = by_name.get(category_name.casefold()) if category_name else None

        if category is None and category_id_raw:
            try:
                category = by_id.get(int(category_id_raw))
            except ValueError:
                return None, f"Invalid category_id '{category_id_raw}'"
            if category is None:
                return None, f"Category ID {category_id_raw} not found"
        if category is None:
            return None, "Missing category (provide 'category' name or 'category_id')"
        if category["type"] != tx_type:
            return None, (
                f"Category '{category['name']}' is type '{category['type']}', "
                f"not '{tx_type}'"
            )

        amount_raw = row.get("amount", "").strip()
        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return None, f"Invalid amount '{amount_raw}'"

        date = row.get("date", "").strip()
        if not validate_date(date):
            return None, f"Invalid date '{date}' (expected YYYY-MM-DD)"

        return {
            "type": tx_type,
            "category_id": category["id"],
            "amount": amount,
            "currency": row.get("currency", "PKR").strip().upper() or "PKR",
            "date": date,
            "description": row.get("description", "").strip() or None,
        }, None

    @staticmethod
    def _category_summary(categories):
        return [
            {"id": category["id"], "name": category["name"], "type": category["type"]}
            for category in categories
        ]

    def analyze(self, user_id, file_bytes):
        rows = parse_csv(file_bytes)
        categories = self._categories.get_categories(user_id)
        expected_columns = list(get_expected_columns())
        if not rows:
            return {
                "total_rows": 0,
                "columns_found": [],
                "columns_missing": expected_columns,
                "valid_rows": 0,
                "invalid_rows": 0,
                "preview": [],
                "categories_available": self._category_summary(categories),
            }

        columns_found = list(rows[0])
        valid_rows = []
        invalid_rows = []
        for row_number, row in enumerate(rows, start=2):
            parsed, error = self._validate_row(row, categories)
            if error:
                invalid_rows.append({"row": row_number, "reason": error})
            else:
                valid_rows.append({"row": row_number, **parsed})

        return {
            "total_rows": len(rows),
            "columns_found": columns_found,
            "columns_missing": [
                column for column in expected_columns if column not in columns_found
            ],
            "valid_rows": len(valid_rows),
            "invalid_rows": len(invalid_rows),
            "preview": valid_rows[:5],
            "errors": invalid_rows[:10],
            "categories_available": self._category_summary(categories),
        }

    async def import_rows(self, user_id, file_bytes):
        rows = parse_csv(file_bytes)
        categories = self._categories.get_categories(user_id)
        imported = 0
        duplicates = 0
        failed = []

        for row_number, row in enumerate(rows, start=2):
            parsed, error = self._validate_row(row, categories)
            if error:
                failed.append({"row": row_number, "reason": error})
                continue
            if self._transactions.transaction_exists(
                user_id,
                parsed["type"],
                parsed["category_id"],
                parsed["amount"],
                parsed["date"],
                parsed["description"],
            ):
                duplicates += 1
                continue

            transaction = TransactionCreate(**parsed)
            try:
                await self._transaction_writer(user_id, transaction)
                imported += 1
            except HTTPException as exc:
                failed.append({"row": row_number, "reason": str(exc)})

        return {
            "imported": imported,
            "duplicates": duplicates,
            "failed": failed,
            "total_rows": len(rows),
        }

    def export(self, user_id):
        transactions = self._transactions.get_transactions(user_id)
        categories = self._categories.get_categories(user_id)
        category_names = {
            category["id"]: category["name"] for category in categories
        }
        return build_csv(transactions, category_names)


_service = CsvImportExportService(
    category_repository,
    transaction_repository,
    add_transaction,
)


def analyze_csv(user_id, file_bytes):
    return _service.analyze(user_id, file_bytes)


async def import_csv(user_id, file_bytes):
    return await _service.import_rows(user_id, file_bytes)


def export_csv(user_id):
    return _service.export(user_id)
