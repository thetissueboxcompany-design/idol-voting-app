# ~/idol_voting/backend/schemas.py

from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


# --- Enums (HIGHLIGHT: New section) ---
class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"
    others = "Others"
    
# # --- User Auth Schemas ---
# class MobileNumberRequest(BaseModel):
    # mobile_number: str
    
    
    
# --- User Auth Schemas (HIGHLIGHT: Major updates) ---
class IdentifierRequest(BaseModel):
    mobile_number: Optional[str] = None
    email: Optional[str] = None

    # HIGHLIGHT: Updated validator logic for more robust checking
    @model_validator(mode='before')
    def check_at_least_one_identifier(cls, values):
        # This logic explicitly checks if a valid mobile number or email is present.
        if 'mobile_number' in values and values['mobile_number']:
            return values
        if 'email' in values and values['email']:
            return values
        raise ValueError('Either mobile_number or email must be provided')
        
        
class OTPVerifyRequest(BaseModel):
    mobile_number: Optional[str] = None
    email: Optional[str] = None
    otp_code: str
class UserBase(BaseModel):
    mobile_number: Optional[str] = None
    email: Optional[str] = None
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
    # HIGHLIGHT: Changed gender from str to our new Enum
    gender: GenderEnum
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
    # HIGHLIGHT: Add a list to accept contestant IDs
    contestant_ids: List[int] = []
class VotingLine(VotingLineBase):
    id: int
    is_active: bool
    # HIGHLIGHT: Include the full contestant objects in the response
    contestants: List[Contestant] = []
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




# --- Vote History Schemas (HIGHLIGHT: New section) ---
class VoteHistoryDetail(BaseModel):
    voting_line_name: str
    voting_line_dates: str  # Formatted as "Month Day, Year - Month Day, Year"
    contestant_name: str
    vote_count: int
    voted_at: datetime

class VoteHistoryResponse(BaseModel):
    history: List[VoteHistoryDetail]
    
    

# --- General Schemas ---
class StatusResponse(BaseModel):
    status: str
    message: str
class Token(BaseModel):
    access_token: str
    token_type: str
