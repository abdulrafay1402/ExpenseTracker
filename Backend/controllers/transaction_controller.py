from models import transaction_model, category_model, settings_model
from utils.exceptions import ValidationError, NotFoundError
from utils.validators import validate_date
from services.currency_api_service import get_exchange_rate
from config import LOCAL_USER_ID


async def add_transaction(user_id, tx_data):
    """Validate and add a new transaction."""
    # Validate date
    if not validate_date(tx_data.date):
        raise ValidationError("Invalid date format. Use YYYY-MM-DD.")

    # Validate category exists and type matches
    if not category_model.category_exists(user_id, tx_data.category_id, tx_data.type):
        raise ValidationError(
            f"Category {tx_data.category_id} does not exist or type mismatch for '{tx_data.type}'."
        )

    # Determine exchange rate
    base_currency = "PKR"
    if tx_data.currency.upper() == base_currency:
        rate = 1.0
    else:
        rate = await get_exchange_rate(tx_data.currency.upper(), base_currency)
        if rate is None:
            # Fallback: check settings for last known rate
            fallback_key = f"rate_{tx_data.currency.upper()}_{base_currency}"
            cached = settings_model.get_setting(user_id, fallback_key)
            if cached:
                rate = float(cached)
            else:
                raise ValidationError(
                    f"Unable to fetch rate for {tx_data.currency} to {base_currency}."
                )
        else:
            # Cache the rate for future fallback
            settings_model.set_setting(
                user_id,
                f"rate_{tx_data.currency.upper()}_{base_currency}",
                str(rate)
            )

    record = transaction_model.add_transaction(
        user_id=user_id,
        type=tx_data.type,
        category_id=tx_data.category_id,
        amount=tx_data.amount,
        currency=tx_data.currency.upper(),
        rate_to_base=rate,
        date=tx_data.date,
        description=tx_data.description,
        payment_method_id=tx_data.payment_method_id
    )
    return record


def list_transactions(user_id, type=None, category_id=None, start_date=None,
                      end_date=None, search=None):
    """List transactions with optional filters."""
    return transaction_model.get_transactions(
        user_id, type=type, category_id=category_id,
        start_date=start_date, end_date=end_date, search=search
    )


def get_transaction(user_id, transaction_id):
    """Get a single transaction by ID."""
    tx = transaction_model.get_transaction_by_id(user_id, transaction_id)
    if not tx:
        raise NotFoundError(f"Transaction {transaction_id} not found.")
    return tx


async def update_transaction(user_id, transaction_id, update_data):
    """Validate and update a transaction."""
    existing = transaction_model.get_transaction_by_id(user_id, transaction_id)
    if not existing:
        raise NotFoundError(f"Transaction {transaction_id} not found.")

    fields = update_data.model_dump(exclude_unset=True)

    # If currency is being updated, recalculate rate
    if "currency" in fields and fields["currency"]:
        base_currency = "PKR"
        curr = fields["currency"].upper()
        if curr == base_currency:
            fields["rate_to_base"] = 1.0
        else:
            rate = await get_exchange_rate(curr, base_currency)
            if rate is None:
                raise ValidationError(f"Unable to fetch rate for {curr}.")
            fields["rate_to_base"] = rate
        fields["currency"] = curr

    # If type changed, validate category still matches
    if "type" in fields and fields["type"] and "category_id" in fields and fields["category_id"]:
        if not category_model.category_exists(user_id, fields["category_id"], fields["type"]):
            raise ValidationError("Category type mismatch.")

    if "date" in fields and fields["date"] and not validate_date(fields["date"]):
        raise ValidationError("Invalid date format. Use YYYY-MM-DD.")

    result = transaction_model.update_transaction(user_id, transaction_id, **fields)
    if not result:
        raise NotFoundError(f"Transaction {transaction_id} not found after update.")
    return result


def void_transaction(user_id, transaction_id):
    """Soft-delete a transaction."""
    existing = transaction_model.get_transaction_by_id(user_id, transaction_id)
    if not existing:
        raise NotFoundError(f"Transaction {transaction_id} not found.")
    return transaction_model.void_transaction(user_id, transaction_id)
