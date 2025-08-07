# ~/idol_voting/backend/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variables
# Example for PostgreSQL: "postgresql://user:password@host:port/database"
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the SQLAlchemy engine
# The engine is the starting point for any SQLAlchemy application.
engine = create_engine(DATABASE_URL)

# Each instance of the SessionLocal class will be a new database session.
# The session is the primary interface for all database operations.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# We will inherit from this class to create each of the ORM models.
Base = declarative_base()

# Dependency to get a DB session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
