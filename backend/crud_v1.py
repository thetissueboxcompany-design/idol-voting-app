# ~/idol_voting/backend/crud.py

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

import models
import schemas

def get_user_by_mobile(db: Session, mobile_number: str):
    """Fetches a user from the database by their mobile number."""
    return db.query(models.User).filter(models.User.mobile_number == mobile_number).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Creates a new user in the database."""
    db_user = models.User(mobile_number=user.mobile_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_otp_for_mobile(db: Session, mobile_number: str):
    """Generates and stores a new OTP for a given mobile number."""
    # Generate a 6-digit OTP
    otp_code = str(random.randint(100000, 999999))
    
    # Set an expiry time (e.g., 5 minutes from now)
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

    # In a real app, you would send the OTP via an SMS gateway here.
    # For now, we'll just print it to the console for testing.
    print(f"OTP for {mobile_number}: {otp_code}")

    return db_otp

def verify_otp(db: Session, mobile_number: str, otp_code: str):
    """Verifies the provided OTP for a given mobile number."""
    # Find the most recent, unused OTP for this mobile number
    db_otp = db.query(models.OTP).filter(
        models.OTP.mobile_number == mobile_number,
        models.OTP.otp_code == otp_code,
        models.OTP.is_used == False,
        models.OTP.expiry_timestamp > datetime.utcnow()
    ).order_by(models.OTP.created_at.desc()).first()

    if not db_otp:
        return None # OTP is invalid, used, or expired

    # Mark the OTP as used
    db_otp.is_used = True
    db.commit()
    db.refresh(db_otp)
    
    return db_otp
