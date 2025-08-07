# ~/idol_voting/backend/main.py

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
import crud
# HIGHLIGHT: Importing the new security module
import security
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Indian Idol Voting API",
    description="API for managing votes, contestants, and users.",
    version="1.0.0"
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/auth/send-otp", response_model=schemas.StatusResponse)
def send_otp(request: schemas.MobileNumberRequest, db: Session = Depends(get_db)):
    crud.create_otp_for_mobile(db, mobile_number=request.mobile_number)
    return {"status": "success", "message": "OTP sent successfully."}

@app.post("/api/auth/verify-otp", response_model=schemas.Token)
def verify_otp_and_login(request: schemas.OTPVerifyRequest, db: Session = Depends(get_db)):
    verified_otp = crud.verify_otp(db, mobile_number=request.mobile_number, otp_code=request.otp_code)

    if not verified_otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")

    user = crud.get_user_by_mobile(db, mobile_number=request.mobile_number)
    if not user:
        user = crud.create_user(db, user=schemas.UserCreate(mobile_number=request.mobile_number))

    # HIGHLIGHT: Create a real JWT instead of a fake one.
    # The 'sub' (subject) of the token is the user's mobile number.
    access_token = security.create_access_token(
        data={"sub": user.mobile_number}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Indian Idol Voting API!"}
