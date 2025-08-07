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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login")
oauth2_scheme_user = OAuth2PasswordBearer(tokenUrl="/api/auth/verify-otp")

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

async def get_current_user(token: str = Depends(oauth2_scheme_user), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"},)
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        # HIGHLIGHT: The JWT subject is now the user ID
        user_id: int = payload.get("sub")
        if user_id is None or payload.get("type") != "user": raise credentials_exception
        user = db.query(models.User).filter(models.User.id == user_id).first()
    except (JWTError, ValueError): raise credentials_exception
    if user is None: raise credentials_exception
    return user

# --- User Auth Endpoints (HIGHLIGHT: Updated) ---
@app.post("/api/auth/send-otp", response_model=schemas.StatusResponse)
def send_otp(request: schemas.IdentifierRequest, db: Session = Depends(get_db)):
    """Generates and sends an OTP to the user's mobile or email."""
    crud.create_otp(db, mobile=request.mobile_number, email=request.email)
    return {"status": "success", "message": "OTP sent successfully."}

@app.post("/api/auth/verify-otp", response_model=schemas.Token)
def verify_otp_and_login(request: schemas.OTPVerifyRequest, db: Session = Depends(get_db)):
    """Verifies OTP and returns a token."""
    verified_otp = crud.verify_otp(db, otp_code=request.otp_code, mobile=request.mobile_number, email=request.email)
    if not verified_otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
    
    user = crud.get_user_by_identifier(db, mobile=request.mobile_number, email=request.email)
    if not user:
        user_data = schemas.UserCreate(mobile_number=request.mobile_number, email=request.email)
        user = crud.create_user(db, user=user_data)
    
    # Use the unique user ID as the subject of the token
    access_token = security.create_access_token(data={"sub": str(user.id), "type": "user"})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Admin, Contestant, Voting Line, Voting, Dashboard, and History endpoints remain the same ---
@app.post("/api/admin/login", response_model=schemas.Token)
def admin_login(form_data: schemas.AdminLoginRequest, db: Session = Depends(get_db)):
    admin = crud.get_admin_by_username(db, username=form_data.username)
    if not admin or not security.verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = security.create_access_token(data={"sub": admin.username, "type": "admin"})
    return {"access_token": access_token, "token_type": "bearer"}
@app.post("/api/admin/contestants", response_model=schemas.Contestant, status_code=status.HTTP_201_CREATED)
def create_new_contestant(name: str = Form(...), age: int = Form(...), gender: str = Form(...), details: str = Form(None), image: UploadFile = File(None), db: Session = Depends(get_db), current_admin: models.Admin = Depends(get_current_admin)):
    image_url = f"images/{image.filename}" if image else None
    contestant_data = schemas.ContestantCreate(name=name, age=age, gender=gender, details=details, image_url=image_url)
    return crud.create_contestant(db=db, contestant=contestant_data)
@app.get("/api/contestants", response_model=List[schemas.Contestant])
def get_all_contestants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_contestants(db, skip=skip, limit=limit)
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
@app.get("/api/vote/state", response_model=schemas.PublicVotingPage)
def get_voting_page_state(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    active_line = crud.get_active_voting_line(db)
    if not active_line: raise HTTPException(status_code=404, detail="Voting is currently closed.")
    contestants = active_line.contestants
    user_votes_cast = crud.get_user_votes_for_line(db, user_id=current_user.id, voting_line_id=active_line.id)
    return {"voting_line": active_line, "contestants": contestants, "user_total_votes": user_votes_cast}
@app.post("/api/vote/submit", response_model=schemas.StatusResponse)
def submit_user_votes(request: schemas.VoteSubmitRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    active_line = crud.get_active_voting_line(db)
    if not active_line: raise HTTPException(status_code=403, detail="Voting is currently closed.")
    total_new_votes = sum(request.votes.values())
    if total_new_votes <= 0: raise HTTPException(status_code=400, detail="No votes to submit.")
    user_votes_cast = crud.get_user_votes_for_line(db, user_id=current_user.id, voting_line_id=active_line.id)
    if (user_votes_cast + total_new_votes) > active_line.max_votes_per_user: raise HTTPException(status_code=400, detail="Vote limit exceeded.")
    crud.submit_votes(db, user_id=current_user.id, voting_line_id=active_line.id, votes=request.votes)
    return {"status": "success", "message": "Votes submitted successfully."}
@app.get("/api/vote/history", response_model=schemas.VoteHistoryResponse)
def get_user_history(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    history_records = crud.get_user_vote_history(db, user_id=current_user.id)
    formatted_history = []
    for record in history_records:
        date_format = "%B %d, %Y"
        date_range = f"{record.start_time.strftime(date_format)} - {record.end_time.strftime(date_format)}"
        formatted_history.append(schemas.VoteHistoryDetail(voting_line_name=record.voting_line_name, voting_line_dates=date_range, contestant_name=record.contestant_name, vote_count=record.vote_count, voted_at=record.created_at))
    return {"history": formatted_history}
@app.get("/api/admin/dashboard-stats/{line_id}", response_model=schemas.DashboardStats)
def get_stats_for_dashboard(line_id: int, db: Session = Depends(get_db), current_admin: models.Admin = Depends(get_current_admin)):
    voting_line = crud.get_voting_line_by_id(db, line_id=line_id)
    if not voting_line: raise HTTPException(status_code=404, detail="Voting line not found.")
    stats = crud.get_dashboard_stats(db, voting_line_id=line_id)
    return {"voting_line_name": voting_line.name, "stats": stats}
@app.get("/")
def read_root():
    return {"message": "Welcome to the Indian Idol Voting API!"}
