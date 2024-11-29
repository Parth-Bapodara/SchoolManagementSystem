from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Database.database import get_db
from src.api.v1.security.security import JWTBearer
from src.api.v1.user.services.CRUD.user_retrieval import UserService, DEFAULT_PAGE, DEFAULT_LIMIT

router = APIRouter()

@router.get("/admins/")
async def get_admins(db: Session = Depends(get_db), token: str = Depends(JWTBearer()), page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT):
    """Fetch admins from the database."""
    return UserService.get_users_by_role(db, token, "admin", page, limit)

@router.get("/students/")
async def get_students(db: Session = Depends(get_db), token: str = Depends(JWTBearer()), page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT):
    """Fetch students from the database."""
    return UserService.get_users_by_role(db, token, "student", page, limit)

@router.get("/teachers/")
async def get_teachers(db: Session = Depends(get_db), token: str = Depends(JWTBearer()), page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT):
    """Fetch teachers from the database."""
    return UserService.get_users_by_role(db, token, "teacher", page, limit)
