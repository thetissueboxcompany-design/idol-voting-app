# ~/idol_voting/backend/crud.py

from sqlalchemy.orm import Session
from sqlalchemy import update, func, desc
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
    db_otp = db.query(models.OTP).filter(models.OTP.mobile_number == mobile_number, models.OTP.otp_code == otp_code, models.OTP.is_used == False, models.OTP.expiry_timestamp > datetime.utcnow()).order_by(models.OTP.created_at.desc()).first()
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
def get_voting_line_by_id(db: Session, line_id: int):
    return db.query(models.VotingLine).filter(models.VotingLine.id == line_id).first()
    #HIGHLIGHT: Updated create_voting_line function
def create_voting_line(db: Session, voting_line: schemas.VotingLineCreate):
    """Creates a new voting line and associates contestants with it."""
    # Separate contestant_ids from the rest of the data
    line_data = voting_line.model_dump(exclude={"contestant_ids"})
    db_voting_line = models.VotingLine(**line_data)
    
    # Fetch the contestant objects from the database
    if voting_line.contestant_ids:
        contestants = db.query(models.Contestant).filter(models.Contestant.id.in_(voting_line.contestant_ids)).all()
        db_voting_line.contestants.extend(contestants)
        
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

# --- Voting Functions ---
def get_active_voting_line(db: Session):
    now = datetime.now(datetime.utcnow().astimezone().tzinfo)
    return db.query(models.VotingLine).filter(models.VotingLine.is_active == True, models.VotingLine.start_time <= now, models.VotingLine.end_time >= now).first()
def get_user_votes_for_line(db: Session, user_id: int, voting_line_id: int):
    total_votes = db.query(func.sum(models.Vote.vote_count)).filter(models.Vote.user_id == user_id, models.Vote.voting_line_id == voting_line_id).scalar()
    return total_votes or 0
def submit_votes(db: Session, user_id: int, voting_line_id: int, votes: dict):
    for contestant_id, vote_count in votes.items():
        if vote_count > 0:
            db_vote = models.Vote(user_id=user_id, contestant_id=int(contestant_id), voting_line_id=voting_line_id, vote_count=vote_count)
            db.add(db_vote)
    db.commit()

# --- Dashboard Functions (HIGHLIGHT: New section) ---
def get_dashboard_stats(db: Session, voting_line_id: int):
    """Calculates the vote count for each contestant for a given voting line."""
    results = db.query(
        models.Contestant.id,
        models.Contestant.name,
        func.sum(models.Vote.vote_count).label('total_votes')
    ).join(
        models.Vote, models.Contestant.id == models.Vote.contestant_id
    ).filter(
        models.Vote.voting_line_id == voting_line_id
    ).group_by(
        models.Contestant.id
    ).order_by(
        desc('total_votes')
    ).all()
    
    return [
        {"contestant_id": r[0], "contestant_name": r[1], "total_votes": r[2] or 0}
        for r in results
    ]
