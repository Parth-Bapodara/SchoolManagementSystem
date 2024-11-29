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
    This helper function uses the decode_access_token to decode the token and extract user data.
    It will return the user data that can be used throughout your routes.
    """
    user_data = security.decode_access_token(token)  # Decode the token using the decode_access_token method
    return user_data  # You can now use this user data throughout your routes

@router.post("/user/create/")
async def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db), 
    user_data: dict = Depends(security.JWTBearer())
):
    """
    Create a new user.
    Only an admin can create a new user.
    """
    # Pass the raw JWT token to the service method
    return UserServices.create_user(db=db, user_data=user, token=user_data)

@router.get("/user/me", response_model=UserInDb)
async def read_user_info(
    db: Session = Depends(get_db), 
    user_data: dict = Depends(security.JWTBearer())
):
    """
    Get the current user's info based on the token
    """
    return UserServices.get_user_info(db=db, token=user_data)

@router.delete("/user/{user_id}/")
async def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    user_data: dict = Depends(security.JWTBearer())  # This will decode the token
):
    """
    Delete a user by ID
    Only admins can delete users.
    """
    # Call the service to delete the user
    return UserServices.delete_user(db=db, user_id=user_id, user_data=user_data)
