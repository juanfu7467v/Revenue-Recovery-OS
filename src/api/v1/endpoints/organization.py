
from fastapi import APIRouter, Depends, HTTPException
from src.utils.auth import get_current_user
from src.services.vault import VaultService
from pydantic import BaseModel

router = APIRouter()

class APIKeyUpdate(BaseModel):
    processor: str # "stripe" o "adyen"
    api_key: str

@router.post("/vault/api-key")
async def update_api_key(data: APIKeyUpdate, current_user: dict = Depends(get_current_user)):
    org_id = current_user["org_id"]
    if not org_id:
        raise HTTPException(status_code=400, detail="User not associated with an organization")
    
    success = VaultService.store_api_key(org_id, data.processor, data.api_key)
    if success:
        return {"message": f"API Key for {data.processor} stored securely in the vault"}
    else:
        raise HTTPException(status_code=500, detail="Failed to store API Key")

@router.get("/me")
async def get_org_details(current_user: dict = Depends(get_current_user)):
    return {"user_id": current_user["user_id"], "org_id": current_user["org_id"]}
