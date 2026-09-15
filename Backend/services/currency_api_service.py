import httpx
from config import CURRENCY_API_BASE

# Curated list for the app's PKR-centric users. open.er-api.com serves 160+
# currencies (incl. SAR/PKR/AED) but no names endpoint, so names live here.
SUPPORTED_CURRENCIES = {
    "PKR": "Pakistani Rupee",
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "SAR": "Saudi Riyal",
    "AED": "UAE Dirham",
    "INR": "Indian Rupee",
    "CNY": "Chinese Yuan",
    "JPY": "Japanese Yen",
    "KRW": "South Korean Won",
    "CAD": "Canadian Dollar",
    "AUD": "Australian Dollar",
    "CHF": "Swiss Franc",
    "TRY": "Turkish Lira",
    "KWD": "Kuwaiti Dinar",
    "QAR": "Qatari Riyal",
    "OMR": "Omani Rial",
    "BHD": "Bahraini Dinar",
    "MYR": "Malaysian Ringgit",
    "THB": "Thai Baht",
    "SGD": "Singapore Dollar",
    "RUB": "Russian Ruble",
}


async def get_supported_currencies():
    """Return the currency list shown in the app. Static and offline-safe."""
    return dict(SUPPORTED_CURRENCIES)


async def get_exchange_rate(base, target):
    """Fetch live exchange rate from open.er-api.com. Returns None on failure.

    Previous provider (Frankfurter) only served ~30 ECB currencies and
    rejected SAR/PKR/AED outright, breaking SAR->PKR conversions.
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{CURRENCY_API_BASE}/latest/{base.upper()}"
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("result") == "success":
                return data.get("rates", {}).get(target.upper())
            return None
    except Exception:
        return None
