# ~/idol_voting/backend/models.py

from sqlalchemy import (Column, Integer, String, DateTime, Boolean, ForeignKey, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Each class here represents a table in the database.

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, unique=True, index=True, nullable=False)
    # HIGHLIGHT: Timestamps are handled automatically by the database server.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Establish a relationship to the votes table
    votes = relationship("Vote", back_populates="user")

class Contestant(Base):
    __tablename__ = "contestants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    image_url = Column(String, nullable=True) # URL to the uploaded picture
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Establish a relationship to the votes table
    votes = relationship("Vote", back_populates="contestant")

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

class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    # HIGHLIGHT: Foreign keys link this table to users and contestants.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contestant_id = Column(Integer, ForeignKey("contestants.id"), nullable=False)
    voting_line_id = Column(Integer, ForeignKey("voting_lines.id"), nullable=False)
    vote_count = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Establish relationships to the user and contestant tables
    user = relationship("User", back_populates="votes")
    contestant = relationship("Contestant", back_populates="votes")


class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, index=True, nullable=False)
    otp_code = Column(String, nullable=False)
    expiry_timestamp = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
