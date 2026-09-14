import httpx
from config import CURRENCY_API_BASE

# In-memory cache: lasts for the lifetime of the server process
_supported_cache = None


async def get_supported_currencies():
    """Fetch supported currencies from Frankfurter API. Cached per session."""
    global _supported_cache
    if _supported_cache is not None:
        return _supported_cache

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{CURRENCY_API_BASE}/currencies")
            resp.raise_for_status()
            _supported_cache = resp.json()
            return _supported_cache
    except Exception:
        # Return a minimal fallback set if API is unreachable
        return {
            "PKR": "Pakistani Rupee",
            "USD": "US Dollar",
            "EUR": "Euro",
            "GBP": "British Pound",
            "AED": "UAE Dirham",
            "SAR": "Saudi Riyal",
            "INR": "Indian Rupee"
        }


async def get_exchange_rate(base, target):
    """Fetch live exchange rate from Frankfurter. Returns None on failure."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{CURRENCY_API_BASE}/latest",
                params={"base": base, "symbols": target}
            )
            resp.raise_for_status()
            data = resp.json()
            return data["rates"].get(target)
    except Exception:
        return None
