from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.api.v1.security import security  
from src.api.v1.exam.models.class_subject_model import Class, Subject
from src.api.v1.exam.schemas.class_subject_schema import ClassCreate, SubjectCreate
from src.api.v1.exam.services.class_management import ClassSubjectServices
from Database.database import get_db
from src.api.v1.security.security import JWTBearer

router = APIRouter()

# Route to create a new class
@router.post("/create_class")
def create_class(class_data: ClassCreate, db: Session = Depends(get_db), user_data: dict = Depends(security.get_logged_user)):
    """
    Create a new class. Only accessible by admin or teacher.
    """
    return ClassSubjectServices.create_class(db, class_data, user_data)

# Route to get all classes
@router.get("/get_classes")
def get_classes(page: int , limit: int, db: Session = Depends(get_db), user_data: dict = Depends(security.get_logged_user), query: str = Query()):
    """
    Get all classes. Only accessible by admin or teacher.
    """
    return ClassSubjectServices.get_all_classes(db, user_data, page, limit, query)

# Route to create a new subject
@router.post("/create_subject")
def create_subject(subject_data: SubjectCreate, db: Session = Depends(get_db), user_data: dict = Depends(security.get_logged_user)):
    """
    Create a new subject. Only accessible by admin or teacher.
    """
    return ClassSubjectServices.create_subject(db, subject_data, user_data)

# Route to get all subjects
@router.get("/get_subjects")
def get_subjects(page: int, limit: int, db: Session = Depends(get_db), user_data: dict = Depends(security.get_logged_user),query: str = Query()):
    """
    Get all subjects. Only accessible by admin or teacher.
    """
    return ClassSubjectServices.get_all_subjects(db, user_data, page, limit, query)
