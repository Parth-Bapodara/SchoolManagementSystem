from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.api.v1.security import security  # JWTBearer used here
from src.api.v1.exam.models.class_subject_model import Class
from src.api.v1.exam.schemas.class_subject_schema import ClassCreate
from src.api.v1.exam.services.class_management import ClassSubjectServices
from Database.database import get_db
from src.api.v1.security.security import JWTBearer

router = APIRouter()

# This function will extract and decode the JWT token, returning the user data.
async def get_current_user(token: str = Depends(security.JWTBearer()), db: Session = Depends(get_db)):
    """
    Decodes the JWT token and returns the user data.
    """
    user_data = security.decode_jwt(token)  # Decode token and extract user data
    return user_data 

@router.post("/create_class")
def create_class(class_data: ClassCreate, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    """
    Create a new class. Only accessible by admin or teacher.
    """
    return ClassSubjectServices.create_class(db, class_data, user_data)

@router.get("/get_classes")
def get_classes(page: int, limit: int, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    """
    Get all classes. Only accessible by admin or teacher.
    """
    return ClassSubjectServices.get_all_classes(db, user_data, page, limit)
