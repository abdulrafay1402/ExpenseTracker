from pydantic import BaseModel, Field
from typing import Optional


class BudgetCreate(BaseModel):
    category_id: int
    amount: float = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)
    alert_threshold: float = Field(80, ge=1, le=100)


class BudgetUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    alert_threshold: Optional[float] = Field(None, ge=1, le=100)


class BudgetResponse(BaseModel):
    id: int
    user_id: str
    category_id: int
    amount: float
    month: int
    year: int
    alert_threshold: float

    model_config = {"from_attributes": True}


class AlertResponse(BaseModel):
    category_id: int
    category_name: Optional[str] = None
    budget_limit: float
    spent: float
    percentage: float
    status: str  # "normal", "warning", "exceeded"
