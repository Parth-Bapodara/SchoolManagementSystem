from sqlalchemy.orm import Session
from src.api.v1.user.models.user_models import User
from src.api.v1.authentication import security
from Database.database import get_db
from sqlalchemy.exc import SQLAlchemyError 

def seed_admin(db: Session):
    """
    Seeds the database with a default admin user if it doesn't already exist.
    """
    if not db.query(User).filter(User.role == "admin").first():
        hashed_password = security.get_password_hash("DefaultAdmin@123")
        default_admin = User(
            email="admin@default.com",
            hashed_password=hashed_password,
            username="defaultAdmin",
            passcode="admin_passcode",
            role="admin",
            status="active"
        )
        db.add(default_admin)
        db.commit()
        db.refresh(default_admin)
        print("Default admin user created.")
    else:
        print("Admin user already exists.")

def seed_data():
    """
    Calls the individual seed functions to populate the database with initial data.
    """
    db: Session = next(get_db())  
    try:
        seed_admin(db)
        print("Database seeding completed.")

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error occurred during seeding: {e}")
        
    finally:
        db.close()