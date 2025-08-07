# ~/idol_voting/backend/crud.py

from sqlalchemy.orm import Session
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
    db_otp = models.OTP(
        mobile_number=mobile_number,
        otp_code=otp_code,
        expiry_timestamp=expiry_time,
        is_used=False
    )
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

    if not db_otp:
        return None
    db_otp.is_used = True
    db.commit()
    db.refresh(db_otp)
    return db_otp

# --- Admin Functions ---
def get_admin_by_username(db: Session, username: str):
    """Fetches an admin by username."""
    return db.query(models.Admin).filter(models.Admin.username == username).first()

# --- Contestant Functions ---
def get_contestants(db: Session, skip: int = 0, limit: int = 100):
    """Fetches all contestants."""
    return db.query(models.Contestant).offset(skip).limit(limit).all()

def create_contestant(db: Session, contestant: schemas.ContestantCreate):
    """Creates a new contestant."""
    db_contestant = models.Contestant(**contestant.model_dump())
    db.add(db_contestant)
    db.commit()
    db.refresh(db_contestant)
    return db_contestant
