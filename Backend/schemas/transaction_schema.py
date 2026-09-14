from pydantic import BaseModel, Field
from typing import Optional


class TransactionCreate(BaseModel):
    type: str = Field(..., pattern="^(income|expense)$")
    category_id: int
    amount: float = Field(..., gt=0)
    currency: str = "PKR"
    date: str  # ISO format: YYYY-MM-DD
    description: Optional[str] = None
    payment_method_id: Optional[int] = None


class TransactionUpdate(BaseModel):
    type: Optional[str] = Field(None, pattern="^(income|expense)$")
    category_id: Optional[int] = None
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    payment_method_id: Optional[int] = None


class TransactionResponse(BaseModel):
    id: int
    user_id: str
    type: str
    category_id: Optional[int] = None
    amount: float
    currency: str
    rate_to_base: float
    date: str
    description: Optional[str] = None
    payment_method_id: Optional[int] = None
    created_at: Optional[str] = None
    voided: int

    model_config = {"from_attributes": True}
