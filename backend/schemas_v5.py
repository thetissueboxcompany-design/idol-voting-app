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

# --- Voting Schemas ---
class VoteSubmitRequest(BaseModel):
    votes: Dict[int, int] = Field(..., example={1: 10, 2: 40})
class PublicVotingPage(BaseModel):
    voting_line: VotingLine
    contestants: List[Contestant]
    user_total_votes: int

# --- Dashboard Schemas (HIGHLIGHT: New section) ---
class ContestantVoteStat(BaseModel):
    contestant_id: int
    contestant_name: str
    total_votes: int

class DashboardStats(BaseModel):
    voting_line_name: str
    stats: List[ContestantVoteStat]


# --- General Schemas ---
class StatusResponse(BaseModel):
    status: str
    message: str
class Token(BaseModel):
    access_token: str
    token_type: str
