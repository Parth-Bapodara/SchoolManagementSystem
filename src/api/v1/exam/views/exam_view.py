from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.v1.exam.schemas.exam_schemas import ExamCreate, ExamUpdate
from src.api.v1.exam.services.exam_management import ExamManagementServices
from Database.database import get_db
from src.api.v1.security import security

router = APIRouter()

@router.post("/exams/")
async def create_exam(exam_data: ExamCreate, db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    """
    Create a new exam
    """
    return ExamManagementServices.create_exam(db, exam_data, token)

@router.get("/exams/")
async def get_all_exams(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    """
    Get all exams
    """
    return ExamManagementServices.get_all_exams(db, token)

@router.put("/exams/{exam_id}")
async def update_exam(exam_id: int, exam_update: ExamUpdate, db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    """
    Update an existing exam
    """
    return ExamManagementServices.update_exam(db, exam_id, exam_update, token)

@router.delete("/exams/{exam_id}")
async def delete_exam(exam_id: int, db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    """
    Delete an exam by ID
    """
    return ExamManagementServices.delete_exam(db, exam_id, token)
