import unittest
from unittest.mock import AsyncMock, Mock

from services.budget_service import BudgetService
from services.csv_service import CsvImportExportService
from services.report_service import top_expenses


class CsvImportExportServiceTests(unittest.TestCase):
    def setUp(self):
        self.categories = Mock()
        self.transactions = Mock()
        self.writer = AsyncMock()
        self.service = CsvImportExportService(
            self.categories, self.transactions, self.writer
        )
        self.categories.get_categories.return_value = [
            {"id": 3, "name": "Food", "type": "expense"},
            {"id": 1, "name": "Salary", "type": "income"},
        ]

    def test_analyze_preserves_row_numbers_and_name_matching(self):
        result = self.service.analyze(
            "user-1",
            b"type,category,amount,date\nexpense,food,25,2026-10-03\n",
        )

        self.assertEqual(result["total_rows"], 1)
        self.assertEqual(result["valid_rows"], 1)
        self.assertEqual(result["preview"][0]["row"], 2)
        self.assertEqual(result["preview"][0]["category_id"], 3)

    def test_analyze_reports_invalid_category_type(self):
        result = self.service.analyze(
            "user-1",
            b"type,category,amount,date\nexpense,Salary,25,2026-10-03\n",
        )

        self.assertEqual(result["invalid_rows"], 1)
        self.assertIn("not 'expense'", result["errors"][0]["reason"])

    def test_import_skips_duplicates_and_imports_valid_new_rows(self):
        self.transactions.transaction_exists.side_effect = [True, False]

        import asyncio

        result = asyncio.run(
            self.service.import_rows(
                "user-1",
                (
                    b"type,category,amount,date\n"
                    b"expense,Food,25,2026-10-03\n"
                    b"income,Salary,100,2026-10-04\n"
                ),
            )
        )

        self.assertEqual(result["imported"], 1)
        self.assertEqual(result["duplicates"], 1)
        self.assertEqual(result["failed"], [])
        self.writer.assert_awaited_once()


class BudgetServiceTests(unittest.TestCase):
    def setUp(self):
        self.budgets = Mock()
        self.categories = Mock()
        self.transactions = Mock()
        self.service = BudgetService(
            self.budgets, self.categories, self.transactions
        )

    def test_alert_uses_shared_threshold_rules(self):
        self.budgets.get_budget_by_category.return_value = {
            "amount": 500,
            "alert_threshold": 80,
        }
        self.transactions.get_sum_by_category_and_month.return_value = 400
        self.categories.get_category_by_id.return_value = {
            "name": "Food",
        }

        alert = self.service.check_alert("user-1", 4, 10, 2026)

        self.assertEqual(alert["status"], "warning")
        self.assertEqual(alert["percentage"], 80)
        self.assertEqual(alert["category_name"], "Food")

    def test_all_alerts_return_unknown_when_category_is_missing(self):
        self.budgets.get_budgets.return_value = [
            {
                "category_id": 8,
                "amount": 100,
                "alert_threshold": 80,
            }
        ]
        self.transactions.get_sum_by_category_and_month.return_value = 120
        self.categories.get_category_by_id.return_value = None

        alerts = self.service.check_all_alerts("user-1", 10, 2026)

        self.assertEqual(alerts[0]["status"], "exceeded")
        self.assertEqual(alerts[0]["category_name"], "Unknown")


class TopExpensesFeatureTests(unittest.TestCase):
    def test_ranked_expenses_use_base_currency_amount(self):
        from unittest.mock import patch

        transactions = [
            {
                "id": 1,
                "category_id": 1,
                "amount": 100,
                "rate_to_base": 1,
                "currency": "PKR",
                "date": "2026-10-02",
                "description": "Small PKR expense",
            },
            {
                "id": 2,
                "category_id": 2,
                "amount": 50,
                "rate_to_base": 3,
                "currency": "USD",
                "date": "2026-10-03",
                "description": "Large converted expense",
            },
        ]
        with (
            patch(
                "services.report_service.transaction_repository.get_month_expense_transactions",
                return_value=transactions,
            ),
            patch(
                "services.report_service.category_repository.get_categories",
                return_value=[
                    {"id": 1, "name": "Food"},
                    {"id": 2, "name": "Travel"},
                ],
            ),
        ):
            result = top_expenses("user-1", 10, 2026, limit=1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 2)
        self.assertEqual(result[0]["base_amount"], 150)
        self.assertEqual(result[0]["category_name"], "Travel")


if __name__ == "__main__":
    unittest.main()
