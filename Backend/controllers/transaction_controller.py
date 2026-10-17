from services import transaction_service


async def add_transaction(user_id, transaction):
    return await transaction_service.add_transaction(user_id, transaction)


def list_transactions(
    user_id, type=None, category_id=None, start_date=None, end_date=None, search=None
):
    return transaction_service.list_transactions(
        user_id,
        type=type,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        search=search,
    )


def get_transaction(user_id, transaction_id):
    return transaction_service.get_transaction(user_id, transaction_id)


async def update_transaction(user_id, transaction_id, transaction):
    return await transaction_service.update_transaction(
        user_id, transaction_id, transaction
    )


def void_transaction(user_id, transaction_id):
    return transaction_service.void_transaction(user_id, transaction_id)
