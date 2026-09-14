from fastapi import FastAPI
from models.database import create_tables
from routes import (
    transaction_routes, category_routes, budget_routes,
    report_routes, currency_routes, csv_routes, backup_routes
)

app = FastAPI(title="ExpenseMate API")

# Create tables and seed data on startup
create_tables()

# Include all routers
app.include_router(transaction_routes.router)
app.include_router(category_routes.router)
app.include_router(budget_routes.router)
app.include_router(report_routes.router)
app.include_router(currency_routes.router)
app.include_router(csv_routes.router)
app.include_router(backup_routes.router)
