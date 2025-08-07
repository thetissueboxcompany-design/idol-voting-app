# ~/idol_voting/backend/schemas.py

from pydantic import BaseModel
from datetime import datetime

# --- User Auth Schemas ---
class MobileNumberRequest(BaseModel):
    mobile_number: str

class OTPVerifyRequest(BaseModel):
    mobile_number: str
    otp_code: str

class UserBase(BaseModel):
    mobile_number: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    class Config:
        from_attributes = True

# --- Admin Auth Schemas (HIGHLIGHT: New section) ---
class AdminLoginRequest(BaseModel):
    username: str
    password: str

# --- Contestant Schemas (HIGHLIGHT: New section) ---
class ContestantBase(BaseModel):
    name: str
    age: int
    gender: str
    details: str | None = None
    image_url: str | None = None

class ContestantCreate(ContestantBase):
    pass

class Contestant(ContestantBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    class Config:
        from_attributes = True

# --- General Schemas ---
class StatusResponse(BaseModel):
    status: str
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str
