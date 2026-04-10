
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

class BrandingSettings(BaseModel):
    logo_url: Optional[str] = None
    primary_color: str = "#3b82f6"  # Default blue
    secondary_color: str = "#1e293b" # Default slate
    tone: str = "professional"      # professional, friendly, urgent
    company_name: Optional[str] = None

class DashboardMetrics(BaseModel):
    recovered_amount: float
    reduction_in_collection_days: float
    accounts_at_risk: int
    monthly_recovered: float = 0.0
    recovery_rate: float = 0.0
    active_recovery_campaigns: int = 0
    message_summary: str = ""

class PreDunningNotification(BaseModel):
    customer_id: str
    customer_email: str
    card_last4: str
    expiry_month: int
    expiry_year: int
    days_until_expiry: int
