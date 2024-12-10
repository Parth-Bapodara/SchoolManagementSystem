from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.v1.user.schemas.user_schemas import UserCreate, UserUpdate, UserInDb
from src.api.v1.user.services.CRUD.user_managment import UserServices,DEFAULT_LIMIT,DEFAULT_PAGE
from Database.database import get_db
from src.api.v1.security import security

router = APIRouter()
  
@router.post("/user/create/")
async def create_user(user: UserCreate, db: Session = Depends(get_db), user_data: dict = Depends(security.JWTBearer())):
    """
    Create a new user.
    Only an admin can create a new user.
    """
    return UserServices.create_user(db=db, user_data=user, token=user_data)

@router.get("/user/me", response_model=UserInDb)
async def read_user_info(db: Session = Depends(get_db), user_data: dict = Depends(security.JWTBearer())):
    """
    Get the current user's info based on the token
    """
    return UserServices.get_user_info(db=db, token=user_data)

@router.delete("/user/{user_id}/")
async def delete_user(user_id: int, db: Session = Depends(get_db), user_data: dict = Depends(security.get_logged_user)):
    """
    Delete a user by ID.
    Only admins can delete users.
    """
    return UserServices.delete_user(db=db, user_id=user_id, user_data=user_data)

@router.get("/admins/")
async def get_admins(db: Session = Depends(get_db), token: str = Depends(security.JWTBearer()), page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT):
    """Fetch admins from the database."""
    return UserServices.get_users_by_role(db, token, "admin", page, limit)

@router.get("/students/")
async def get_students(db: Session = Depends(get_db), token: str = Depends(security.JWTBearer()), page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT):
    """Fetch students from the database."""
    return UserServices.get_users_by_role(db, token, "student", page, limit)

@router.get("/teachers/")
async def get_teachers(db: Session = Depends(get_db), token: str = Depends(security.JWTBearer()), page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT):
    """Fetch teachers from the database."""
    return UserServices.get_users_by_role(db, token, "teacher", page, limit)