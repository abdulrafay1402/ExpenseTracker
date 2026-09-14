from fastapi import APIRouter, Query
from typing import Optional
from config import LOCAL_USER_ID
from schemas.transaction_schema import TransactionCreate, TransactionUpdate, TransactionResponse
from controllers import transaction_controller

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse)
async def add_transaction(tx: TransactionCreate):
    return await transaction_controller.add_transaction(LOCAL_USER_ID, tx)


@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    type: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    return transaction_controller.list_transactions(
        LOCAL_USER_ID, type=type, category_id=category_id,
        start_date=start_date, end_date=end_date, search=search
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int):
    return transaction_controller.get_transaction(LOCAL_USER_ID, transaction_id)


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction_id: int, tx: TransactionUpdate):
    return await transaction_controller.update_transaction(LOCAL_USER_ID, transaction_id, tx)


@router.delete("/{transaction_id}", response_model=TransactionResponse)
def void_transaction(transaction_id: int):
    return transaction_controller.void_transaction(LOCAL_USER_ID, transaction_id)
