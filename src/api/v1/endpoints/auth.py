
from fastapi import APIRouter, Depends, HTTPException, status
from src.utils.auth import get_current_user

router = APIRouter()

@router.get("/validate-token")
async def validate_token(current_user: dict = Depends(get_current_user)):
    """
    Endpoint para validar si un token es válido.
    Retorna información básica de la empresa asociada.
    """
    return {
        "valid": True,
        "company_name": current_user.get("company_name"),
        "org_id": current_user.get("org_id")
    }
