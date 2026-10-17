from fastapi import APIRouter, Query
from typing import Optional
from config import LOCAL_USER_ID
from schemas.category_schema import CategoryCreate, CategoryUpdate, CategoryResponse
from services import category_service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(type: Optional[str] = Query(None)):
    return category_service.list_categories(LOCAL_USER_ID, type=type)


@router.post("", response_model=CategoryResponse)
def add_category(cat: CategoryCreate):
    return category_service.add_category(LOCAL_USER_ID, cat.name, cat.type)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, cat: CategoryUpdate):
    return category_service.update_category(LOCAL_USER_ID, category_id, cat.name)


@router.delete("/{category_id}")
def delete_category(category_id: int):
    return category_service.delete_category(LOCAL_USER_ID, category_id)
