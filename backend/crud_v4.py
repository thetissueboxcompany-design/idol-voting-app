# ~/idol_voting/backend/crud.py

from sqlalchemy.orm import Session
from sqlalchemy import update, func
from datetime import datetime, timedelta
import random

import models
import schemas
import security

# --- User Functions ---
def get_user_by_mobile(db: Session, mobile_number: str):
    return db.query(models.User).filter(models.User.mobile_number == mobile_number).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(mobile_number=user.mobile_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- OTP Functions ---
def create_otp_for_mobile(db: Session, mobile_number: str):
    otp_code = str(random.randint(100000, 999999))
    expiry_time = datetime.utcnow() + timedelta(minutes=5)
    db_otp = models.OTP(mobile_number=mobile_number, otp_code=otp_code, expiry_timestamp=expiry_time, is_used=False)
    db.add(db_otp)
    db.commit()
    db.refresh(db_otp)
    print(f"OTP for {mobile_number}: {otp_code}")
    return db_otp

def verify_otp(db: Session, mobile_number: str, otp_code: str):
    db_otp = db.query(models.OTP).filter(
        models.OTP.mobile_number == mobile_number,
        models.OTP.otp_code == otp_code,
        models.OTP.is_used == False,
        models.OTP.expiry_timestamp > datetime.utcnow()
    ).order_by(models.OTP.created_at.desc()).first()
    if not db_otp: return None
    db_otp.is_used = True
    db.commit()
    db.refresh(db_otp)
    return db_otp

# --- Admin Functions ---
def get_admin_by_username(db: Session, username: str):
    return db.query(models.Admin).filter(models.Admin.username == username).first()

# --- Contestant Functions ---
def get_contestants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contestant).offset(skip).limit(limit).all()

def create_contestant(db: Session, contestant: schemas.ContestantCreate):
    db_contestant = models.Contestant(**contestant.model_dump())
    db.add(db_contestant)
    db.commit()
    db.refresh(db_contestant)
    return db_contestant

# --- Voting Line Functions ---
def get_voting_lines(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.VotingLine).order_by(models.VotingLine.created_at.desc()).offset(skip).limit(limit).all()

def create_voting_line(db: Session, voting_line: schemas.VotingLineCreate):
    db_voting_line = models.VotingLine(**voting_line.model_dump())
    db.add(db_voting_line)
    db.commit()
    db.refresh(db_voting_line)
    return db_voting_line

def update_voting_line_status(db: Session, line_id: int, is_active: bool):
    if is_active:
        db.execute(update(models.VotingLine).values(is_active=False))
    db.execute(update(models.VotingLine).where(models.VotingLine.id == line_id).values(is_active=is_active))
    db.commit()
    return db.query(models.VotingLine).filter(models.VotingLine.id == line_id).first()

# --- Voting Functions (HIGHLIGHT: New section) ---
def get_active_voting_line(db: Session):
    """Fetches the currently active voting line."""
    now = datetime.now(datetime.utcnow().astimezone().tzinfo)
    return db.query(models.VotingLine).filter(
        models.VotingLine.is_active == True,
        models.VotingLine.start_time <= now,
        models.VotingLine.end_time >= now
    ).first()

def get_user_votes_for_line(db: Session, user_id: int, voting_line_id: int):
    """Calculates the total votes a user has cast for a specific voting line."""
    total_votes = db.query(func.sum(models.Vote.vote_count)).filter(
        models.Vote.user_id == user_id,
        models.Vote.voting_line_id == voting_line_id
    ).scalar()
    return total_votes or 0

def submit_votes(db: Session, user_id: int, voting_line_id: int, votes: dict):
    """Saves a user's votes to the database."""
    for contestant_id, vote_count in votes.items():
        if vote_count > 0:
            db_vote = models.Vote(
                user_id=user_id,
                contestant_id=int(contestant_id),
                voting_line_id=voting_line_id,
                vote_count=vote_count
            )
            db.add(db_vote)
    db.commit()
