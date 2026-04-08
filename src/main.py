
from fastapi import FastAPI
from src.api.v1.endpoints import webhooks, dashboard

app = FastAPI(title="Cashflow Recovery API", version="0.1.0")

app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to Cashflow Recovery API!"}

