from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from src.database.firestore import db
from src.utils.auth import get_password_hash, verify_password, create_access_token
from src.config import settings
from pydantic import BaseModel, EmailStr

router = APIRouter()

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    company_name: str

@router.post("/register")
async def register(user: UserRegister):
    if not db:
        raise HTTPException(status_code=503, detail="Database connection not available.")
    
    try:
        user_ref = db.collection("users").document(user.email).get()
        if user_ref.exists:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        org_ref = db.collection("organizations").document()
        org_id = org_ref.id
        org_ref.set({
            "name": user.company_name,
            "plan": "free",
            "status": "active",
            "created_at": datetime.utcnow()
        })
        
        hashed_password = get_password_hash(user.password)
        db.collection("users").document(user.email).set({
            "email": user.email,
            "hashed_password": hashed_password,
            "org_id": org_id,
            "is_active": True
        })
        
        return {"message": "User and organization created successfully", "org_id": org_id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during registration: {e}")
        raise HTTPException(status_code=500, detail="Error creating user.")

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not db:
        raise HTTPException(status_code=503, detail="Database connection not available.")
    
    try:
        user_doc = db.collection("users").document(form_data.username).get()
        if not user_doc.exists:
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        
        user_data = user_doc.to_dict()
        if not verify_password(form_data.password, user_data["hashed_password"]):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data["email"], "org_id": user_data["org_id"]},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Error during authentication.")
