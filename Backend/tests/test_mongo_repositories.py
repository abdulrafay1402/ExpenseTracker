import unittest
import re
from unittest.mock import patch

from repositories import transaction_repository


class FakeCursor(list):
    def sort(self, sort_spec):
        for key, direction in reversed(sort_spec):
            super().sort(
                key=lambda row: row.get(key),
                reverse=direction < 0,
            )
        return self


class FakeCollection:
    def __init__(self, documents):
        self.documents = documents
        self.last_query = None

    def find(self, query, projection=None):
        self.last_query = query
        matched = []
        for document in self.documents:
            if not self._matches(document, query):
                continue
            matched.append(dict(document))
        if projection:
            included = {key for key, enabled in projection.items() if enabled}
            matched = [
                {key: value for key, value in row.items() if key in included or key == "_id"}
                for row in matched
            ]
        return FakeCursor(matched)

    @classmethod
    def _matches(cls, document, query):
        for key, expected in query.items():
            if key == "$or":
                if not any(cls._matches(document, clause) for clause in expected):
                    return False
                continue
            actual = document.get(key)
            if isinstance(expected, dict):
                if "$regex" in expected:
                    if not re.search(expected["$regex"], str(actual or "")):
                        return False
                if "$gte" in expected and (
                    actual is None or actual < expected["$gte"]
                ):
                    return False
                if "$lte" in expected and (
                    actual is None or actual > expected["$lte"]
                ):
                    return False
                if "$in" in expected and actual not in expected["$in"]:
                    return False
            elif actual != expected:
                return False
        return True


class MongoRepositoryTests(unittest.TestCase):
    def test_dashboard_totals_sum_base_currency_and_count_nonvoided_rows(self):
        collection = FakeCollection(
            [
                {
                    "user_id": "user-1",
                    "voided": 0,
                    "date": "2026-10-01",
                    "type": "income",
                    "amount": 100,
                    "rate_to_base": 1,
                },
                {
                    "user_id": "user-1",
                    "voided": 0,
                    "date": "2026-10-02",
                    "type": "expense",
                    "amount": 20,
                    "rate_to_base": 2,
                },
                {
                    "user_id": "user-1",
                    "voided": 1,
                    "date": "2026-10-03",
                    "type": "expense",
                    "amount": 50,
                    "rate_to_base": 1,
                },
            ]
        )

        with patch(
            "repositories.transaction_repository.get_collection",
            return_value=collection,
        ):
            result = transaction_repository.get_dashboard_totals(
                "user-1", 10, 2026
            )

        self.assertEqual(
            result,
            {
                "total_income": 100,
                "total_expenses": 40,
                "transaction_count": 2,
            },
        )

    def test_monthly_trend_groups_by_month_and_type(self):
        collection = FakeCollection(
            [
                {
                    "user_id": "user-1",
                    "voided": 0,
                    "date": "2026-02-01",
                    "type": "expense",
                    "amount": 10,
                    "rate_to_base": 1,
                },
                {
                    "user_id": "user-1",
                    "voided": 0,
                    "date": "2026-02-15",
                    "type": "expense",
                    "amount": 20,
                    "rate_to_base": 2,
                },
                {
                    "user_id": "user-1",
                    "voided": 0,
                    "date": "2026-01-15",
                    "type": "income",
                    "amount": 100,
                    "rate_to_base": 1,
                },
            ]
        )

        with patch(
            "repositories.transaction_repository.get_collection",
            return_value=collection,
        ):
            result = transaction_repository.get_monthly_trend("user-1", 2026)

        self.assertEqual(
            result,
            [
                {"month": 1, "type": "income", "total": 100},
                {"month": 2, "type": "expense", "total": 50},
            ],
        )


if __name__ == "__main__":
    unittest.main()
