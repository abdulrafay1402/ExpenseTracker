from services.currency_api_service import get_supported_currencies, get_exchange_rate
from models import settings_model
from utils.exceptions import ValidationError


async def get_currencies(user_id):
    """Return the list of supported currencies."""
    currencies = await get_supported_currencies()
    return {"currencies": currencies}


async def get_rate(user_id, base, target):
    """Get exchange rate between two currencies with fallback."""
    base = base.upper()
    target = target.upper()

    if base == target:
        return {"base": base, "target": target, "rate": 1.0}

    rate = await get_exchange_rate(base, target)
    if rate is not None:
        # Cache for fallback
        settings_model.set_setting(user_id, f"rate_{base}_{target}", str(rate))
        return {"base": base, "target": target, "rate": rate}

    # Fallback to cached rate
    cached = settings_model.get_setting(user_id, f"rate_{base}_{target}")
    if cached:
        return {"base": base, "target": target, "rate": float(cached)}

    raise ValidationError(f"Unable to fetch rate for {base} to {target}.")
