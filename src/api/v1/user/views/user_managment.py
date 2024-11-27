from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.v1.user.schemas.user_schemas import UserCreate,UserUpdate,UserInDb
from src.api.v1.user.services.CRUD.user_managment import UserServices
from Database.database import get_db
from src.api.v1.security import security

router = APIRouter()

@router.post("/user/create/")
async def create_user(user: UserCreate, db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    """
    Create a new user
    """
    return UserServices.create_user(db=db, user_data=user, token=token)

@router.put("/user/update-info/", response_model=UserInDb)
async def update_user_info(user_update: UserUpdate, db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    """
    Update user information like password
    """
    return UserServices.update_user_info(db=db, user_update=user_update, token=token)

@router.get("/user/me", response_model=UserInDb)
async def read_user_info(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    """
    Get the current user's info based on the token
    """
    return UserServices.get_user_info(db=db, token=token)

@router.delete("/user/{user_id}/")
async def delete_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    """
    Delete a user by ID
    """
    return UserServices.delete_user(db=db, user_id=user_id, token=token)