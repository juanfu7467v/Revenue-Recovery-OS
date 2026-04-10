from fastapi import FastAPI
from src.api.v1.endpoints import webhooks, dashboard, auth, organization, processors

app = FastAPI(title="Cashflow Recovery API", version="0.1.0")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(organization.router, prefix="/api/v1/organization", tags=["Organization"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(processors.router, prefix="/api/v1/webhooks/processors", tags=["Payment Processors Webhooks"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to Cashflow Recovery API!"}
