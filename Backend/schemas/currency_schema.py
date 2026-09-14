from pydantic import BaseModel
from typing import Dict, Optional


class CurrencyListResponse(BaseModel):
    currencies: Dict[str, str]


class RateResponse(BaseModel):
    base: str
    target: str
    rate: float
