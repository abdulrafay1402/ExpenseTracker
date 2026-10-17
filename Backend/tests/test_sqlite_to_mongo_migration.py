import sqlite3
import tempfile
import unittest
from pathlib import Path

from Backend.scripts.migrate_sqlite_to_mongo import (
    MigrationError,
    migrate_sqlite_to_mongo,
)


class FakeCollection:
    def __init__(self):
        self.documents = {}

    def find_one(self, query):
        document = self.documents.get(query["_id"])
        return dict(document) if document is not None else None

    def insert_one(self, document):
        self.documents[document["_id"]] = dict(document)


class FakeDatabase:
    def __init__(self):
        self.collections = {}

    def list_collection_names(self):
        return list(self.collections)

    def create_collection(self, name):
        self.collections[name] = FakeCollection()

    def __getitem__(self, name):
        return self.collections[name]


class SqliteToMongoMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sqlite_path = Path(self.temp_dir.name) / "source.db"
        connection = sqlite3.connect(self.sqlite_path)
        try:
            connection.executescript(
                """
                CREATE TABLE users (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    created_at TEXT
                );
                CREATE TABLE transactions (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT,
                    amount REAL,
                    voided INTEGER
                );
                INSERT INTO users VALUES ('user-01', 'ExpenseMate user', NULL);
                INSERT INTO transactions VALUES (7, 'user-01', 1250.5, 0);
                """
            )
        finally:
            connection.close()
        self.database = FakeDatabase()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_copies_rows_preserving_primary_keys_and_values(self):
        result = migrate_sqlite_to_mongo(self.sqlite_path, self.database)

        self.assertEqual(result["users"]["verified"], 1)
        self.assertEqual(result["transactions"]["inserted"], 1)
        self.assertEqual(
            self.database["transactions"].find_one({"_id": 7}),
            {
                "_id": 7,
                "id": 7,
                "user_id": "user-01",
                "amount": 1250.5,
                "voided": 0,
            },
        )

    def test_rerunning_is_idempotent_for_identical_records(self):
        migrate_sqlite_to_mongo(self.sqlite_path, self.database)

        result = migrate_sqlite_to_mongo(self.sqlite_path, self.database)

        self.assertEqual(result["users"]["inserted"], 0)
        self.assertEqual(result["users"]["already_present"], 1)
        self.assertEqual(result["transactions"]["verified"], 1)

    def test_refuses_to_replace_conflicting_target_record(self):
        self.database.create_collection("users")
        self.database["users"].insert_one(
            {"_id": "user-01", "id": "user-01", "name": "Different", "created_at": None}
        )

        with self.assertRaisesRegex(MigrationError, "different data"):
            migrate_sqlite_to_mongo(self.sqlite_path, self.database)

        self.assertEqual(
            self.database["users"].find_one({"_id": "user-01"})["name"],
            "Different",
        )

    def test_rejects_table_without_single_primary_key(self):
        connection = sqlite3.connect(self.sqlite_path)
        try:
            connection.execute("CREATE TABLE invalid_table (value TEXT)")
        finally:
            connection.close()

        with self.assertRaisesRegex(MigrationError, "exactly one primary key"):
            migrate_sqlite_to_mongo(self.sqlite_path, self.database)

    def test_rejects_missing_source_file(self):
        missing_path = Path(self.temp_dir.name) / "missing.db"

        with self.assertRaisesRegex(MigrationError, "does not exist"):
            migrate_sqlite_to_mongo(missing_path, self.database)

    def test_rejects_empty_database(self):
        empty_path = Path(self.temp_dir.name) / "empty.db"
        sqlite3.connect(empty_path).close()

        with self.assertRaisesRegex(MigrationError, "No application tables"):
            migrate_sqlite_to_mongo(empty_path, self.database)


if __name__ == "__main__":
    unittest.main()
