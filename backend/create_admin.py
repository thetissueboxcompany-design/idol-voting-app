# ~/idol_voting/backend/create_admin.py
import sys
from getpass import getpass
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import security

# Create all tables if they don't exist
models.Base.metadata.create_all(bind=engine)

def create_admin_user(db: Session, username: str, password: str):
    """Creates a new admin user in the database."""
    # Check if admin already exists
    db_admin = db.query(models.Admin).filter(models.Admin.username == username).first()
    if db_admin:
        print(f"Error: Admin with username '{username}' already exists.")
        return

    hashed_password = security.get_password_hash(password)
    new_admin = models.Admin(username=username, hashed_password=hashed_password)
    db.add(new_admin)
    db.commit()
    print(f"Admin user '{username}' created successfully.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("--- Create Admin User ---")
        # Get username from command line argument or prompt
        admin_username = sys.argv[1] if len(sys.argv) > 1 else input("Enter admin username: ")
        
        # Get password securely without showing it on screen
        admin_password = getpass("Enter admin password: ")
        password_confirm = getpass("Confirm admin password: ")

        if admin_password != password_confirm:
            print("Error: Passwords do not match.")
        elif not admin_username or not admin_password:
            print("Error: Username and password cannot be empty.")
        else:
            create_admin_user(db, username=admin_username, password=admin_password)
    finally:
        db.close()
