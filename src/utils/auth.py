
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from src.database.firestore import db

# Definir el esquema de seguridad usando un Header para el token
# El nombre del header puede ser 'X-Token' o 'Authorization'
# Según la instrucción "Validar cada petición usando un token", usaremos un header simple.
api_key_header = APIKeyHeader(name="X-Token", auto_error=False)

async def get_current_user(token: str = Depends(api_key_header)):
    """
    Valida el token contra la colección 'empresas' en Firestore.
    Busca un documento donde el campo 'token' coincida con el proporcionado.
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
        
        # Mantener compatibilidad con el contrato anterior: devolver user_id y org_id
        # Usamos el ID del documento como org_id y un identificador genérico o el mismo ID como user_id
        org_id = empresa_doc.id
        user_id = empresa_data.get("email", f"user_{org_id}")
        
        return {
            "user_id": user_id,
            "org_id": org_id,
            "company_name": empresa_data.get("nombre", "Empresa")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error validating token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during token validation"
        )
