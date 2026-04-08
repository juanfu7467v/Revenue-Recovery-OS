
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    company_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    created_at: datetime

class TokenBase(BaseModel):
    user_id: str
    processor_name: str
    token_encrypted: str

class RecoveryLogBase(BaseModel):
    user_id: str
    invoice_id: str
    status: str
    amount: float
    currency: str
    retry_count: int
    last_retry_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    created_at: datetime = datetime.now()

class DashboardMetrics(BaseModel):
    recovered_amount: float
    reduction_in_collection_days: float
    accounts_at_risk: int
