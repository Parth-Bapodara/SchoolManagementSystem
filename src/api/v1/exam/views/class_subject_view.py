from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.v1.exam.schemas.class_subject_schema import ClassCreate, SubjectCreate
from src.api.v1.exam.services.class_management import ClassSubjectServices
from Database.database import get_db
from src.api.v1.security import security

router = APIRouter()

@router.post("/classes/")
async def create_class(class_data: ClassCreate, db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    return ClassSubjectServices.create_class(db, class_data, token)

@router.get("/classes/")
async def get_all_classes(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme), page: int = 1, limit:int = 5):
    return ClassSubjectServices.get_all_classes(db, token, page, limit)

@router.post("/subjects/")
async def create_subject(subject_data: SubjectCreate, db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    return ClassSubjectServices.create_subject(db, subject_data, token)

@router.get("/subjects/")
async def get_all_subjects(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme), page:int = 1, limit:int=5):
    return ClassSubjectServices.get_all_subjects(db, token, page, limit)
