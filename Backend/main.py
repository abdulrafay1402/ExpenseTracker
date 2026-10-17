from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from models.database import close_client, create_tables
from routes import (
    transaction_routes, category_routes, budget_routes,
    report_routes, currency_routes, csv_routes, backup_routes
)

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    create_tables()
    try:
        yield
    finally:
        close_client()


app = FastAPI(title="ExpenseMate API", lifespan=lifespan)

# Include all routers
app.include_router(transaction_routes.router)
app.include_router(category_routes.router)
app.include_router(budget_routes.router)
app.include_router(report_routes.router)
app.include_router(currency_routes.router)
app.include_router(csv_routes.router)
app.include_router(backup_routes.router)
