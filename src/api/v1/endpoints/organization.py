
from fastapi import APIRouter, Depends, HTTPException, status
from src.utils.auth import get_current_user
from src.services.vault import VaultService
from pydantic import BaseModel, EmailStr
from src.api.v1.schemas import BrandingSettings, DraftLead
from src.database.firestore import db
from datetime import datetime

router = APIRouter()

class APIKeyUpdate(BaseModel):
    processor: str # "stripe", "mercadopago", etc.
    api_key: str

class ProfileUpdate(BaseModel):
    perfil_dolor: str
    perfil_volumen: str
    perfil_herramientas: str
    perfil_autoridad: str
    perfil_motivacion: str

@router.post("/profile")
async def update_profile(profile: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    """Paso 1: Completar el perfil del usuario"""
    org_id = current_user["org_id"]
    if not db:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    try:
        # Actualizar empresa
        db.collection("empresas").document(org_id).update({
            **profile.dict(),
            "perfilCompletadoAt": datetime.utcnow()
        })
        
        # Actualizar draft_leads
        db.collection("draft_leads").document(org_id).set({
            "step": "perfil",
            "updatedAt": datetime.utcnow()
        })
        
        return {"message": "Profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@router.post("/branding")
async def update_branding(settings: BrandingSettings, current_user: dict = Depends(get_current_user)):
    """Paso 2: Configuración de Branding"""
    org_id = current_user["org_id"]
    if not db:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    try:
        db.collection("empresas").document(org_id).update({
            "branding": settings.dict(),
            "marcaCompletadaAt": datetime.utcnow()
        })
        
        # Actualizar draft_leads
        db.collection("draft_leads").document(org_id).update({
            "step": "marca",
            "updatedAt": datetime.utcnow()
        })
        
        return {"message": "Branding settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update branding: {str(e)}")

@router.get("/branding", response_model=BrandingSettings)
async def get_branding(current_user: dict = Depends(get_current_user)):
    org_id = current_user["org_id"]
    if not db:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    org_doc = db.collection("empresas").document(org_id).get()
    if not org_doc.exists:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    data = org_doc.to_dict()
    branding = data.get("branding", {})
    return BrandingSettings(**branding) if branding else BrandingSettings()

@router.post("/vault/api-key")
async def update_api_key(data: APIKeyUpdate, current_user: dict = Depends(get_current_user)):
    """Paso 3: Configuración de pagos"""
    org_id = current_user["org_id"]
    if not org_id:
        raise HTTPException(status_code=400, detail="User not associated with an organization")
    
    success = VaultService.store_api_key(org_id, data.processor, data.api_key)
    if success:
        # Marcar configuración como completada en la empresa
        if db:
            db.collection("empresas").document(org_id).update({
                "procesador": data.processor,
                "vault_api_key_set": True,
                "configCompletadaAt": datetime.utcnow(),
                "status": "active",
                "activatedAt": datetime.utcnow()
            })
            # El registro en draft_leads ya no es necesario si completó todo, 
            # pero podemos dejarlo o borrarlo. Por ahora lo dejamos como 'completado'.
            db.collection("draft_leads").document(org_id).update({
                "step": "config",
                "updatedAt": datetime.utcnow()
            })
            
        return {"message": f"API Key for {data.processor} stored securely and system activated"}
    else:
        raise HTTPException(status_code=500, detail="Failed to store API Key")

@router.get("/me")
async def get_org_details(current_user: dict = Depends(get_current_user)):
    return current_user
