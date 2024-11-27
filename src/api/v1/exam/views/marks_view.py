from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.v1.exam.schemas.exam_schemas import ExamSubmissionCreate, ExamSubmissionResponse
from src.api.v1.exam.services.marks_managment import ExamSubmissionServices
from Database.database import get_db
from src.api.v1.security import security

router = APIRouter()

@router.post("/exams/{exam_id}/submit/")
async def submit_exam(
    exam_id: int, 
    answers: str, 
    db: Session = Depends(get_db), 
    token: str = Depends(security.oauth2_scheme)
):
    """
    Submit an exam for a student
    """
    return ExamSubmissionServices.take_exam(db, exam_id, answers, token)

@router.put("/exams/{exam_id}/submit/{submission_id}/marks/")
async def update_marks(
    exam_id: int, 
    submission_id: int, 
    marks: float, 
    db: Session = Depends(get_db), 
    token: str = Depends(security.oauth2_scheme)
):
    """
    Update marks for a student's exam submission
    """
    return ExamSubmissionServices.update_marks(db, submission_id, marks, exam_id, token)
