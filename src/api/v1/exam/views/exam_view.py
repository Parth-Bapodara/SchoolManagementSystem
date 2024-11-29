from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from src.api.v1.exam.schemas.exam_schemas import ExamCreate, ExamUpdate
from src.api.v1.exam.services.exam_management import ExamManagementServices
from Database.database import get_db
from src.api.v1.security.security import decode_access_token,JWTBearer  
import logging

router = APIRouter()

async def get_current_user(token: str = Depends(JWTBearer()), db: Session = Depends(get_db)):
    """
    This helper function decodes the JWT token, extracts user data,
    and returns the current user.
    """
    try:
        user_data = decode_access_token(token)  
        return user_data
    except HTTPException as e:
        raise HTTPException(
            status_code=403,
            detail="Invalid token. Could not validate credentials."
        )


@router.post("/create-exam/")
async def create_exam(
    exam_data: ExamCreate, 
    user_data: dict = Depends(get_current_user),  # Assuming you have a function to get the current user
    exam_pdf: UploadFile = File(None),  # Optional file upload
    db: Session = Depends(get_db)
):
    return ExamManagementServices.create_exam(db, exam_data, user_data, exam_pdf)

@router.get("/exams/")
async def get_all_exams(
    db: Session = Depends(get_db), 
    user_data: dict = Depends(get_current_user),
    page: int = 1,
    limit: int = 10
):
    """
    Get all exams with pagination
    """
    return ExamManagementServices.get_all_exams(db, user_data, page, limit)

@router.put("/exams/{exam_id}")
async def update_exam(
    exam_id: int, 
    exam_update: ExamUpdate, 
    db: Session = Depends(get_db), 
    user_data: dict = Depends(get_current_user)
):
    """
    Update an existing exam
    """
    return ExamManagementServices.update_exam(db, exam_id, exam_update, user_data)

@router.delete("/exams/{exam_id}")
async def delete_exam(
    exam_id: int, 
    db: Session = Depends(get_db), 
    user_data: dict = Depends(get_current_user)
):
    """
    Delete an exam by ID
    """
    return ExamManagementServices.delete_exam(db, exam_id, user_data)
