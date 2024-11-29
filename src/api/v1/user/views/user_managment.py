from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.v1.user.schemas.user_schemas import UserCreate, UserUpdate, UserInDb
from src.api.v1.user.services.CRUD.user_managment import UserServices
from Database.database import get_db
from src.api.v1.security import security

router = APIRouter()

# Helper function to extract and verify user data from token
async def get_current_user(token: str = Depends(security.JWTBearer()), db: Session = Depends(get_db)):
    """
    This helper function decodes the JWT token, extracts user data,
    and returns the current user.
    """
    user_data = security.decode_jwt(token)  # Decode token and extract user data
    return user_data  # You can now use this user data throughout your routes

@router.post("/user/create/")
async def create_user(user: UserCreate, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    """
    Create a new user
    """
    return UserServices.create_user(db=db, user_data=user, current_user=user_data)

@router.put("/user/update-info/", response_model=UserInDb)
async def update_user_info(user_update: UserUpdate, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    """
    Update user information like password
    """
    return UserServices.update_user_info(db=db, user_update=user_update, current_user=user_data)

@router.get("/user/me", response_model=UserInDb)
async def read_user_info(db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    """
    Get the current user's info based on the token
    """
    return UserServices.get_user_info(db=db, current_user=user_data)

@router.delete("/user/{user_id}/")
async def delete_user(user_id: int, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    """
    Delete a user by ID
    """
    return UserServices.delete_user(db=db, user_id=user_id, current_user=user_data)
