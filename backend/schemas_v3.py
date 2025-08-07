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

# --- Admin Auth Schemas ---
class AdminLoginRequest(BaseModel):
    username: str
    password: str

# --- Contestant Schemas ---
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

# --- Voting Line Schemas (HIGHLIGHT: New section) ---
class VotingLineBase(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime
    max_votes_per_user: int

class VotingLineCreate(VotingLineBase):
    pass

class VotingLine(VotingLineBase):
    id: int
    is_active: bool
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
