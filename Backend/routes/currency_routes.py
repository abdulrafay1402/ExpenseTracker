from fastapi import APIRouter, Query
from config import LOCAL_USER_ID
from schemas.currency_schema import CurrencyListResponse, RateResponse
from controllers import currency_controller

router = APIRouter(prefix="/currencies", tags=["Currencies"])


@router.get("", response_model=CurrencyListResponse)
async def get_currencies():
    return await currency_controller.get_currencies(LOCAL_USER_ID)


@router.get("/rate", response_model=RateResponse)
async def get_rate(
    base: str = Query(..., description="Base currency code, e.g. USD"),
    target: str = Query(..., description="Target currency code, e.g. PKR")
):
    return await currency_controller.get_rate(LOCAL_USER_ID, base, target)
