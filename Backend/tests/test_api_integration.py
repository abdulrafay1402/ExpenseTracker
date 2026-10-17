import unittest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from main import app
from config import LOCAL_USER_ID


def transaction_record(**overrides):
    record = {
        "id": 101,
        "user_id": LOCAL_USER_ID,
        "type": "expense",
        "category_id": 2,
        "amount": 1250.0,
        "currency": "PKR",
        "rate_to_base": 1.0,
        "date": "2026-10-01",
        "description": "Groceries",
        "payment_method_id": None,
        "created_at": "2026-10-01T12:00:00",
        "voided": 0,
    }
    return {**record, **overrides}


class ExpenseMateApiIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.startup_patch = patch("main.create_tables")
        self.shutdown_patch = patch("main.close_client")
        self.startup_patch.start()
        self.shutdown_patch.start()
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.startup_patch.stop()
        self.shutdown_patch.stop()

    def test_add_expense_request_runs_through_service(self):
        with (
            patch(
                "services.transaction_service.category_repository.category_exists",
                return_value=True,
            ),
            patch(
                "services.transaction_service.transaction_repository.add_transaction",
                return_value=transaction_record(),
            ) as add_transaction,
        ):
            response = self.client.post(
                "/transactions",
                json={
                    "type": "expense",
                    "category_id": 2,
                    "amount": 1250,
                    "currency": "PKR",
                    "date": "2026-10-01",
                    "description": "Groceries",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], 101)
        self.assertEqual(response.json()["rate_to_base"], 1.0)
        add_transaction.assert_called_once()

    def test_category_list_preserves_api_response(self):
        with patch(
            "services.category_service.category_repository.get_categories",
            return_value=[
                {
                    "_id": 2,
                    "id": 2,
                    "user_id": LOCAL_USER_ID,
                    "name": "Food",
                    "type": "expense",
                }
            ],
        ):
            response = self.client.get("/categories?type=expense")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["name"], "Food")

    def test_create_budget_checks_category_and_returns_budget(self):
        budget = {
            "_id": 17,
            "id": 17,
            "user_id": LOCAL_USER_ID,
            "category_id": 2,
            "amount": 5000.0,
            "month": 10,
            "year": 2026,
            "alert_threshold": 80.0,
        }
        with (
            patch(
                "services.budget_service.budget_repository.get_budget_by_category",
                return_value=None,
            ),
            patch(
                "services.budget_service.category_repository.get_category_by_id",
                return_value={"id": 2, "name": "Food", "type": "expense"},
            ),
            patch(
                "services.budget_service.budget_repository.set_budget",
                return_value=budget,
            ) as create_budget,
        ):
            response = self.client.post(
                "/budget",
                json={
                    "category_id": 2,
                    "amount": 5000,
                    "month": 10,
                    "year": 2026,
                    "alert_threshold": 80,
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], 17)
        create_budget.assert_called_once()

    def test_monthly_summary_combines_repository_results(self):
        with (
            patch(
                "services.report_service.transaction_repository.get_dashboard_totals",
                return_value={
                    "total_income": 50000.0,
                    "total_expenses": 12000.0,
                    "transaction_count": 4,
                },
            ),
            patch(
                "services.report_service.category_repository.get_top_expense_category",
                return_value={"category_name": "Food"},
            ),
            patch(
                "services.report_service.transaction_repository.get_category_wise_spending",
                return_value=[
                    {"category_name": "Food", "category_id": 2, "total": 12000.0}
                ],
            ),
        ):
            response = self.client.get(
                "/reports/monthly-summary?month=10&year=2026"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["remaining"], 38000.0)
        self.assertEqual(response.json()["top_expense_category"], "Food")
        self.assertEqual(response.json()["category_breakdown"][0]["total"], 12000.0)

    def test_top_expenses_feature_returns_ranked_report_items(self):
        with patch(
            "services.report_service.top_expenses",
            return_value=[
                {
                    "id": 23,
                    "category_name": "Travel",
                    "base_amount": 15000.0,
                    "currency": "USD",
                    "date": "2026-10-09",
                    "description": "Flight",
                }
            ],
        ) as get_top_expenses:
            response = self.client.get(
                "/reports/top-expenses?month=10&year=2026"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["category_name"], "Travel")
        get_top_expenses.assert_called_once_with(
            LOCAL_USER_ID, month=10, year=2026
        )

    def test_budget_alert_calculates_warning_from_spending(self):
        with (
            patch(
                "services.budget_service.budget_repository.get_budget_by_category",
                return_value={
                    "id": 17,
                    "amount": 5000.0,
                    "alert_threshold": 80.0,
                },
            ),
            patch(
                "services.budget_service.transaction_repository.get_sum_by_category_and_month",
                return_value=4200.0,
            ),
            patch(
                "services.budget_service.category_repository.get_category_by_id",
                return_value={"name": "Food"},
            ),
        ):
            response = self.client.get(
                "/budget/alert/2?month=10&year=2026"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["percentage"], 84.0)
        self.assertEqual(response.json()["status"], "warning")

    def test_csv_import_uses_transaction_service_and_reports_import(self):
        with (
            patch(
                "services.csv_service.category_repository.get_categories",
                return_value=[
                    {"id": 2, "name": "Food", "type": "expense"}
                ],
            ),
            patch(
                "services.csv_service.transaction_repository.transaction_exists",
                return_value=False,
            ),
            patch(
                "services.transaction_service.category_repository.category_exists",
                return_value=True,
            ),
            patch(
                "services.transaction_service.transaction_repository.add_transaction",
                return_value=transaction_record(),
            ) as add_transaction,
        ):
            response = self.client.post(
                "/csv/import",
                files={
                    "file": (
                        "transactions.csv",
                        b"type,category,amount,date\nexpense,Food,1250,2026-10-01\n",
                        "text/csv",
                    )
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["imported"], 1)
        self.assertEqual(response.json()["failed"], [])
        add_transaction.assert_called_once()

    def test_delete_transaction_soft_voids_record(self):
        with (
            patch(
                "services.transaction_service.transaction_repository.get_transaction_by_id",
                return_value=transaction_record(),
            ),
            patch(
                "services.transaction_service.transaction_repository.void_transaction",
                return_value=transaction_record(voided=1),
            ) as void_transaction,
        ):
            response = self.client.delete("/transactions/101")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["voided"], 1)
        void_transaction.assert_called_once_with(LOCAL_USER_ID, 101)

    def test_create_backup_uses_backup_service(self):
        with patch(
            "services.backup_service.backup_database",
            return_value={"detail": "Backup created successfully.", "path": "backup.zip"},
        ) as create_backup:
            response = self.client.post("/backup")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Backup created successfully", response.json()["detail"])
        create_backup.assert_called_once_with()

    def test_restore_latest_backup_matches_flutter_request(self):
        with patch(
            "services.backup_service.restore_latest_backup",
            return_value={"detail": "Database restored successfully from backup."},
        ) as restore_backup:
            response = self.client.post("/backup/restore")

        self.assertEqual(response.status_code, 200)
        self.assertIn("restored successfully", response.json()["detail"])
        restore_backup.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
