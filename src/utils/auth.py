
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from src.database.firestore import db
from datetime import datetime

# Header para el token de la empresa
api_key_header = APIKeyHeader(name="X-Token", auto_error=False)

async def get_current_user(token: str = Depends(api_key_header)):
    """
    Valida el token contra la colección 'empresas' en Firestore.
    Verifica también que el plan del usuario esté vigente.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not db:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available",
        )

    try:
        # Buscar en la colección "empresas", campo "token"
        empresas_ref = db.collection("empresas").where("token", "==", token).limit(1).get()
        
        if not empresas_ref:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        
        # Obtener los datos de la empresa encontrada
        empresa_doc = empresas_ref[0]
        empresa_data = empresa_doc.to_dict()
        
        # VALIDACIÓN DE PLAN
        # El backend debe validar el plan antes de que el sistema empiece a funcionar
        plan_active = empresa_data.get("plan_active", False)
        plan_expires_at = empresa_data.get("plan_expires_at")
        
        # Si el plan no está activo o ha expirado
        is_expired = False
        if plan_expires_at:
            # Firestore devuelve datetime objects
            if datetime.utcnow() > plan_expires_at.replace(tzinfo=None):
                is_expired = True
        
        if not plan_active or is_expired:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Plan inactive or expired. Please renew your subscription.",
            )

        # Retornar datos normalizados para el resto de la app
        return {
            "user_id": empresa_data.get("uid"),
            "org_id": empresa_doc.id,
            "company_name": empresa_data.get("nombre_comercial", empresa_data.get("nombre", "Empresa")),
            "email": empresa_data.get("email"),
            "plan_status": "active"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error validating token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during token validation"
        )

async def validate_plan_by_org_id(org_id: str):
    """
    Utilidad para validar el plan directamente por org_id (usado en webhooks).
    """
    if not db:
        return False
        
    try:
        doc = db.collection("empresas").document(org_id).get()
        if not doc.exists:
            return False
            
        data = doc.to_dict()
        plan_active = data.get("plan_active", False)
        plan_expires_at = data.get("plan_expires_at")
        
        if not plan_active:
            return False
            
        if plan_expires_at and datetime.utcnow() > plan_expires_at.replace(tzinfo=None):
            return False
            
        return True
    except Exception as e:
        print(f"Error validating plan for org {org_id}: {e}")
        return False
