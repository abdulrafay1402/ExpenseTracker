"""MongoDB backup and restore operations."""

import os
import re
import tempfile
import zipfile

from bson import json_util

from config import DB_PATH
from models.database import get_database
from utils.exceptions import NotFoundError


BACKUP_PATH = os.path.join(os.path.dirname(DB_PATH), "expensemate_backup.zip")
_COLLECTION_FILE = re.compile(r"^[A-Za-z0-9_-]+\.json$")


def create_backup():
    """Export all MongoDB collections to an Extended JSON ZIP archive."""
    database = get_database()
    with zipfile.ZipFile(BACKUP_PATH, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(database.list_collection_names()):
            documents = list(database[name].find({}))
            archive.writestr(
                f"{name}.json",
                json_util.dumps(documents, ensure_ascii=False),
            )
    return BACKUP_PATH


def get_backup_path():
    return BACKUP_PATH if os.path.exists(BACKUP_PATH) else None


def restore_latest_backup():
    path = get_backup_path()
    if path is None:
        raise NotFoundError("No database backup is available to restore.")
    with open(path, "rb") as backup_file:
        return restore_database(backup_file.read())


def restore_from_backup(archive_bytes):
    """Validate an Extended JSON archive, then replace its collections."""
    with tempfile.NamedTemporaryFile(suffix=".zip") as temp_file:
        temp_file.write(archive_bytes)
        temp_file.flush()
        with zipfile.ZipFile(temp_file.name) as archive:
            names = archive.namelist()
            if not names or any(
                not _COLLECTION_FILE.fullmatch(name) for name in names
            ):
                raise ValueError("Backup archive contains invalid collection files.")
            documents_by_collection = {}
            for filename in names:
                collection_name = filename[:-5]
                documents = json_util.loads(archive.read(filename))
                if not isinstance(documents, list) or any(
                    not isinstance(document, dict) or "_id" not in document
                    for document in documents
                ):
                    raise ValueError(
                        f"Backup data for '{collection_name}' is invalid."
                    )
                if len({repr(document["_id"]) for document in documents}) != len(documents):
                    raise ValueError(
                        f"Backup data for '{collection_name}' has duplicate IDs."
                    )
                documents_by_collection[collection_name] = documents

    database = get_database()
    collection_names = set(database.list_collection_names())
    restore_names = set(documents_by_collection)
    for name in collection_names - restore_names:
        if name != "system.indexes":
            database[name].delete_many({})
    for name, documents in documents_by_collection.items():
        collection = database[name]
        collection.delete_many({})
        if documents:
            collection.insert_many(documents, ordered=True)

    return True


def backup_database():
    path = create_backup()
    return {"detail": "Backup created successfully.", "path": path}


def restore_database(file_bytes, filename=None):
    if not file_bytes:
        raise ValueError("Backup file is empty.")
    restore_from_backup(file_bytes)
    return {"detail": "Database restored successfully from backup."}
