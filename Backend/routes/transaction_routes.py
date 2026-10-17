from fastapi import APIRouter, Query
from typing import Optional
from config import LOCAL_USER_ID
from schemas.transaction_schema import TransactionCreate, TransactionUpdate, TransactionResponse
from services import transaction_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse)
async def add_transaction(tx: TransactionCreate):
    return await transaction_service.add_transaction(LOCAL_USER_ID, tx)


@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    type: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    return transaction_service.list_transactions(
        LOCAL_USER_ID, type=type, category_id=category_id,
        start_date=start_date, end_date=end_date, search=search
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int):
    return transaction_service.get_transaction(LOCAL_USER_ID, transaction_id)


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction_id: int, tx: TransactionUpdate):
    return await transaction_service.update_transaction(
        LOCAL_USER_ID, transaction_id, tx
    )


@router.delete("/{transaction_id}", response_model=TransactionResponse)
def void_transaction(transaction_id: int):
    return transaction_service.void_transaction(LOCAL_USER_ID, transaction_id)
