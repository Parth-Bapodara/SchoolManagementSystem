from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.v1.user.services.CRUD.user_managment import UserServices
from Database.database import get_db
from src.api.v1.security import security

router = APIRouter()

DEFAULT_PAGE = 1
DEFAULT_LIMIT = 5

@router.get("/admins/")
async def get_admins(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme), page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT):
    """
    Get all admins
    """
    return UserServices.get_users_by_role(db=db, token=token, role="admin", page=page, limit=limit)

@router.get("/students/")
async def get_students(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme), page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT):
    """
    Get all students
    """
    return UserServices.get_users_by_role(db=db, token=token, role="student", page=page, limit=limit)

@router.get("/teachers/")
async def get_teachers(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme), page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT):
    """
    Get all teachers
    """
    return UserServices.get_users_by_role(db=db, token=token, role="teacher", page=page, limit=limit)
