# ~/idol_voting/backend/main.py

import os
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

import models, schemas, crud, security
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Indian Idol Voting API",
    description="API for managing votes, contestants, and users.",
    version="1.0.0"
)

# --- CORS Middleware ---
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ADMIN_FRONTEND_URL = os.getenv("ADMIN_FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, ADMIN_FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Security & Dependencies ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login") # For admin
oauth2_scheme_user = OAuth2PasswordBearer(tokenUrl="/api/auth/verify-otp") # For user

async def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"},)
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None or payload.get("type") != "admin": raise credentials_exception
    except JWTError: raise credentials_exception
    admin = crud.get_admin_by_username(db, username=username)
    if admin is None: raise credentials_exception
    return admin

# HIGHLIGHT: New dependency to get the current logged-in user
async def get_current_user(token: str = Depends(oauth2_scheme_user), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"},)
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        mobile_number: str = payload.get("sub")
        if mobile_number is None or payload.get("type") != "user": raise credentials_exception
    except JWTError: raise credentials_exception
    user = crud.get_user_by_mobile(db, mobile_number=mobile_number)
    if user is None: raise credentials_exception
    return user

# --- User Auth Endpoints ---
@app.post("/api/auth/send-otp", response_model=schemas.StatusResponse)
def send_otp(request: schemas.MobileNumberRequest, db: Session = Depends(get_db)):
    crud.create_otp_for_mobile(db, mobile_number=request.mobile_number)
    return {"status": "success", "message": "OTP sent successfully."}

@app.post("/api/auth/verify-otp", response_model=schemas.Token)
def verify_otp_and_login(request: schemas.OTPVerifyRequest, db: Session = Depends(get_db)):
    verified_otp = crud.verify_otp(db, mobile_number=request.mobile_number, otp_code=request.otp_code)
    if not verified_otp: raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
    user = crud.get_user_by_mobile(db, mobile_number=request.mobile_number)
    if not user: user = crud.create_user(db, user=schemas.UserCreate(mobile_number=request.mobile_number))
    access_token = security.create_access_token(data={"sub": user.mobile_number, "type": "user"})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Admin Endpoints ---
@app.post("/api/admin/login", response_model=schemas.Token)
def admin_login(form_data: schemas.AdminLoginRequest, db: Session = Depends(get_db)):
    admin = crud.get_admin_by_username(db, username=form_data.username)
    if not admin or not security.verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = security.create_access_token(data={"sub": admin.username, "type": "admin"})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Contestant Endpoints ---
@app.post("/api/admin/contestants", response_model=schemas.Contestant, status_code=status.HTTP_201_CREATED)
def create_new_contestant(name: str = Form(...), age: int = Form(...), gender: str = Form(...), details: str = Form(None), image: UploadFile = File(None), db: Session = Depends(get_db), current_admin: models.Admin = Depends(get_current_admin)):
    image_url = f"images/{image.filename}" if image else None
    contestant_data = schemas.ContestantCreate(name=name, age=age, gender=gender, details=details, image_url=image_url)
    return crud.create_contestant(db=db, contestant=contestant_data)

@app.get("/api/contestants", response_model=List[schemas.Contestant])
def get_all_contestants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_contestants(db, skip=skip, limit=limit)

# --- Voting Line Endpoints ---
@app.post("/api/admin/voting-lines", response_model=schemas.VotingLine, status_code=status.HTTP_201_CREATED)
def create_new_voting_line(voting_line: schemas.VotingLineCreate, db: Session = Depends(get_db), current_admin: models.Admin = Depends(get_current_admin)):
    return crud.create_voting_line(db=db, voting_line=voting_line)

@app.get("/api/admin/voting-lines", response_model=List[schemas.VotingLine])
def get_all_voting_lines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_admin: models.Admin = Depends(get_current_admin)):
    return crud.get_voting_lines(db, skip=skip, limit=limit)

@app.patch("/api/admin/voting-lines/{line_id}/activate", response_model=schemas.VotingLine)
def activate_voting_line(line_id: int, db: Session = Depends(get_db), current_admin: models.Admin = Depends(get_current_admin)):
    return crud.update_voting_line_status(db=db, line_id=line_id, is_active=True)

@app.patch("/api/admin/voting-lines/{line_id}/deactivate", response_model=schemas.VotingLine)
def deactivate_voting_line(line_id: int, db: Session = Depends(get_db), current_admin: models.Admin = Depends(get_current_admin)):
    return crud.update_voting_line_status(db=db, line_id=line_id, is_active=False)

# --- Public Voting Endpoints ---
@app.get("/api/vote/state", response_model=schemas.PublicVotingPage)
def get_voting_page_state(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Fetches all data needed for the main voting page."""
    active_line = crud.get_active_voting_line(db)
    if not active_line:
        raise HTTPException(status_code=404, detail="Voting is currently closed.")
    
    contestants = crud.get_contestants(db)
    user_votes_cast = crud.get_user_votes_for_line(db, user_id=current_user.id, voting_line_id=active_line.id)
    
    return {
        "voting_line": active_line,
        "contestants": contestants,
        "user_total_votes": user_votes_cast
    }

@app.post("/api/vote/submit", response_model=schemas.StatusResponse)
def submit_user_votes(
    request: schemas.VoteSubmitRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Submits votes for the current user."""
    active_line = crud.get_active_voting_line(db)
    if not active_line:
        raise HTTPException(status_code=403, detail="Voting is currently closed.")
    
    total_new_votes = sum(request.votes.values())
    if total_new_votes <= 0:
        raise HTTPException(status_code=400, detail="No votes to submit.")
        
    user_votes_cast = crud.get_user_votes_for_line(db, user_id=current_user.id, voting_line_id=active_line.id)
    
    if (user_votes_cast + total_new_votes) > active_line.max_votes_per_user:
        raise HTTPException(status_code=400, detail="Vote limit exceeded.")
        
    crud.submit_votes(db, user_id=current_user.id, voting_line_id=active_line.id, votes=request.votes)
    
    return {"status": "success", "message": "Votes submitted successfully."}

# --- Root Endpoint ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Indian Idol Voting API!"}
