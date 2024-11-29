from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.v1.exam.schemas.exam_schemas import ExamCreate, ExamUpdate
from src.api.v1.exam.services.exam_management import ExamManagementServices
from Database.database import get_db
from src.api.v1.security import security
import logging

router = APIRouter()

# Helper function to extract and verify user data from the token
async def get_current_user(token: str = Depends(security.JWTBearer()), db: Session = Depends(get_db)):
    """
    This helper function decodes the JWT token, extracts user data,
    and returns the current user.
    """
    user_data = security.decode_jwt(token)  # Decode token and extract user data
    return user_data  # You can now use this user data throughout your routes

@router.post("/exams/")
async def create_exam(exam_data: ExamCreate, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    """
    Create a new exam
    """
    return ExamManagementServices.create_exam(db, exam_data, user_data)

@router.get("/exams/")
async def get_all_exams(db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    """
    Get all exams
    """
    return ExamManagementServices.get_all_exams(db, user_data)

@router.put("/exams/{exam_id}")
async def update_exam(exam_id: int, exam_update: ExamUpdate, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    """
    Update an existing exam
    """
    return ExamManagementServices.update_exam(db, exam_id, exam_update, user_data)

@router.delete("/exams/{exam_id}")
async def delete_exam(exam_id: int, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    """
    Delete an exam by ID
    """
    return ExamManagementServices.delete_exam(db, exam_id, user_data)
