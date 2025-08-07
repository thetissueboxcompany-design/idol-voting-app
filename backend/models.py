# ~/idol_voting/backend/models.py

from sqlalchemy import (Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Table, CheckConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

voting_line_contestants = Table('voting_line_contestants', Base.metadata,
    Column('voting_line_id', Integer, ForeignKey('voting_lines.id'), primary_key=True),
    Column('contestant_id', Integer, ForeignKey('contestants.id'), primary_key=True)
)

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint('mobile_number IS NOT NULL OR email IS NOT NULL', name='user_identifier_check'),
    )
    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    votes = relationship("Vote", back_populates="user")

class Contestant(Base):
    __tablename__ = "contestants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    votes = relationship("Vote", back_populates="contestant")
    voting_lines = relationship("VotingLine", secondary=voting_line_contestants, back_populates="contestants")

class VotingLine(Base):
    __tablename__ = "voting_lines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    max_votes_per_user = Column(Integer, default=50)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    contestants = relationship("Contestant", secondary=voting_line_contestants, back_populates="voting_lines")

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contestant_id = Column(Integer, ForeignKey("contestants.id"), nullable=False)
    voting_line_id = Column(Integer, ForeignKey("voting_lines.id"), nullable=False)
    vote_count = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship("User", back_populates="votes")
    contestant = relationship("Contestant", back_populates="votes")

class OTP(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, index=True, nullable=True)
    # HIGHLIGHT: This 'email' column was likely missing from your file
    email = Column(String, index=True, nullable=True)
    otp_code = Column(String, nullable=False)
    expiry_timestamp = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
