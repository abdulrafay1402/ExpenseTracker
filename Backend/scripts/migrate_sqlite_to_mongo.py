"""Copy SQLite tables into MongoDB while preserving their primary keys."""

import argparse
import os
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SQLITE_PATH = BACKEND_DIR / "expense.db"


class MigrationError(RuntimeError):
    """Raised when source data cannot be safely copied or verified."""


def migrate_sqlite_to_mongo(sqlite_path, mongo_database):
    """Copy every user table, preserving SQLite primary keys as MongoDB _id.

    Existing identical documents are accepted so an interrupted migration can
    be rerun. A document with the same key but different data is never replaced.
    """
    sqlite_path = Path(sqlite_path)
    if not sqlite_path.is_file():
        raise MigrationError(f"SQLite source file does not exist: {sqlite_path}")

    summary = {}
    with closing(sqlite3.connect(sqlite_path)) as connection:
        connection.row_factory = sqlite3.Row
        tables = [
            row["name"]
            for row in connection.execute(
                """SELECT name FROM sqlite_master
                   WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                   ORDER BY name"""
            )
        ]
        if not tables:
            raise MigrationError(
                f"No application tables were found in SQLite source: {sqlite_path}"
            )

        for table in tables:
            quoted_table = table.replace('"', '""')
            columns = connection.execute(
                f'PRAGMA table_info("{quoted_table}")'
            ).fetchall()
            primary_keys = [column["name"] for column in columns if column["pk"]]
            if len(primary_keys) != 1:
                raise MigrationError(
                    f"Table '{table}' must have exactly one primary key; "
                    f"found {len(primary_keys)}."
                )
            primary_key = primary_keys[0]

            collection_names = mongo_database.list_collection_names()
            if table not in collection_names:
                mongo_database.create_collection(table)
            collection = mongo_database[table]

            counts = {
                "source": 0,
                "inserted": 0,
                "already_present": 0,
                "verified": 0,
            }
            rows = connection.execute(
                f'SELECT * FROM "{quoted_table}" ORDER BY "{primary_key}"'
            )
            for row in rows:
                document = dict(row)
                record_id = document[primary_key]
                if record_id is None:
                    raise MigrationError(
                        f"Table '{table}' contains a NULL primary key."
                    )
                document["_id"] = record_id
                counts["source"] += 1

                existing = collection.find_one({"_id": record_id})
                if existing is None:
                    collection.insert_one(document)
                    counts["inserted"] += 1
                elif existing != document:
                    raise MigrationError(
                        f"Target collection '{table}' already has different data "
                        f"for primary key {record_id!r}; no document was replaced."
                    )
                else:
                    counts["already_present"] += 1

                if collection.find_one({"_id": record_id}) != document:
                    raise MigrationError(
                        f"Verification failed for '{table}' primary key "
                        f"{record_id!r}."
                    )
                counts["verified"] += 1
            summary[table] = counts

    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Copy SQLite ExpenseMate data into MongoDB."
    )
    parser.add_argument(
        "--sqlite-path",
        type=Path,
        default=DEFAULT_SQLITE_PATH,
        help=f"SQLite database path (default: {DEFAULT_SQLITE_PATH})",
    )
    parser.add_argument(
        "--database",
        default=None,
        help="MongoDB database name (defaults to MONGO_DATABASE or expensemate).",
    )
    args = parser.parse_args(argv)

    load_dotenv(BACKEND_DIR / ".env")
    mongo_uri = os.environ.get("MONGO_URI")
    if not mongo_uri:
        print("MONGO_URI is not set in Backend/.env or the environment.", file=sys.stderr)
        return 2
    database_name = args.database or os.environ.get("MONGO_DATABASE", "expensemate")

    try:
        from pymongo import MongoClient
        from pymongo.errors import PyMongoError
    except ImportError:
        print(
            "PyMongo is required. Install the Backend requirements before migrating.",
            file=sys.stderr,
        )
        return 2

    client = None
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
        client.admin.command("ping")
        summary = migrate_sqlite_to_mongo(args.sqlite_path, client[database_name])
        print(f"Migration verified in MongoDB database '{database_name}':")
        for table, counts in summary.items():
            print(
                f"  {table}: {counts['source']} source rows, "
                f"{counts['verified']} verified "
                f"({counts['inserted']} inserted, "
                f"{counts['already_present']} already present)"
            )
    except PyMongoError as exc:
        print(
            f"MongoDB operation failed ({type(exc).__name__}); "
            "details are suppressed to protect connection credentials.",
            file=sys.stderr,
        )
        return 1
    except (MigrationError, sqlite3.Error, OSError) as exc:
        print(f"Migration failed: {exc}", file=sys.stderr)
        return 1
    finally:
        if client is not None:
            client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
