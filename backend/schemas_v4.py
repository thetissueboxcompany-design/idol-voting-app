# ~/idol_voting/backend/schemas.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict

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

# --- Voting Line Schemas ---
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

# --- Voting Schemas (HIGHLIGHT: New section) ---
class VoteSubmitRequest(BaseModel):
    # The structure will be { "contestant_id": vote_count, ... }
    # e.g., { "1": 10, "3": 5 }
    votes: Dict[int, int] = Field(..., example={1: 10, 2: 40})

# Schema for the public voting page data
class PublicVotingPage(BaseModel):
    voting_line: VotingLine
    contestants: List[Contestant]
    user_total_votes: int

# --- General Schemas ---
class StatusResponse(BaseModel):
    status: str
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str
