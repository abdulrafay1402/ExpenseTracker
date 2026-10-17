from services import currency_service


async def get_currencies(user_id):
    return await currency_service.get_currencies(user_id)


async def get_rate(user_id, base, target):
    return await currency_service.get_rate(user_id, base, target)
