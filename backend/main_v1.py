# ~/idol_voting/backend/main.py

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Importing new modules
import models
import schemas
import crud
from database import engine, get_db

# This command creates all the tables in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Indian Idol Voting API",
    description="API for managing votes, contestants, and users.",
    version="1.0.0"
)

# Adding CORS middleware to allow frontend requests
# This is crucial for connecting the frontend and backend.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Authentication Endpoints ---

@app.post("/api/auth/send-otp", response_model=schemas.StatusResponse)
def send_otp(request: schemas.MobileNumberRequest, db: Session = Depends(get_db)):
    """
    Generates and sends an OTP to the user's mobile number.
    """
    crud.create_otp_for_mobile(db, mobile_number=request.mobile_number)
    return {"status": "success", "message": "OTP sent successfully."}


@app.post("/api/auth/verify-otp", response_model=schemas.Token)
def verify_otp_and_login(request: schemas.OTPVerifyRequest, db: Session = Depends(get_db)):
    """
    Verifies the OTP. If successful, it creates the user if they don't exist
    and returns an access token.
    """
    verified_otp = crud.verify_otp(db, mobile_number=request.mobile_number, otp_code=request.otp_code)

    if not verified_otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")

    # Check if user exists, if not, create one
    user = crud.get_user_by_mobile(db, mobile_number=request.mobile_number)
    if not user:
        user = crud.create_user(db, user=schemas.UserCreate(mobile_number=request.mobile_number))

    # For now, we return a placeholder token.
    # In a later phase, we will implement JWT (JSON Web Tokens) for real security.
    access_token = f"fake-token-for-user-{user.id}"
    return {"access_token": access_token, "token_type": "bearer"}


# --- Root Endpoint ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Indian Idol Voting API!"}
