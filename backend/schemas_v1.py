# ~/idol_voting/backend/schemas.py

from pydantic import BaseModel
from datetime import datetime

# Pydantic model for handling mobile number in request body
class MobileNumberRequest(BaseModel):
    mobile_number: str

# Pydantic model for verifying the OTP
class OTPVerifyRequest(BaseModel):
    mobile_number: str
    otp_code: str

# Base model for a User
class UserBase(BaseModel):
    mobile_number: str

# Model for creating a new user
class UserCreate(UserBase):
    pass

# Model for reading user data (will be sent in API responses)
class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        # This allows Pydantic to work with ORM models (like our SQLAlchemy ones)
        from_attributes = True

# A simple response model for successful operations
class StatusResponse(BaseModel):
    status: str
    message: str

# A model for the token we will issue upon successful login
# We will use this more in the next phase
class Token(BaseModel):
    access_token: str
    token_type: str
