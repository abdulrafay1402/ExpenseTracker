from services import category_service


def list_categories(user_id, type=None):
    return category_service.list_categories(user_id, type=type)


def add_category(user_id, category):
    return category_service.add_category(user_id, category.name, category.type)


def update_category(user_id, category_id, category):
    return category_service.update_category(
        user_id, category_id, category.name
    )


def delete_category(user_id, category_id):
    return category_service.delete_category(user_id, category_id)
