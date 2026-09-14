from models import category_model
from utils.exceptions import ValidationError, NotFoundError, ConflictError


def list_categories(user_id, type=None):
    """List categories with optional type filter."""
    return category_model.get_categories(user_id, type=type)


def add_category(user_id, name, type):
    """Add a new custom category."""
    return category_model.add_category(user_id, name, type)


def update_category(user_id, category_id, name):
    """Rename a category."""
    existing = category_model.get_category_by_id(user_id, category_id)
    if not existing:
        raise NotFoundError(f"Category {category_id} not found.")
    return category_model.update_category(user_id, category_id, name)


def delete_category(user_id, category_id):
    """Delete a category if it's not used by any transaction."""
    existing = category_model.get_category_by_id(user_id, category_id)
    if not existing:
        raise NotFoundError(f"Category {category_id} not found.")
    success = category_model.delete_category(user_id, category_id)
    if not success:
        raise ConflictError(
            f"Category {category_id} is in use by transactions and cannot be deleted."
        )
    return {"detail": "Category deleted successfully."}
