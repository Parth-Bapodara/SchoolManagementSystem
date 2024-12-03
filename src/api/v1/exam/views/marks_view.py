from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.v1.exam.schemas.exam_schemas import ExamSubmissionCreate, ExamSubmissionResponse
from src.api.v1.exam.services.marks_managment import ExamSubmissionServices
from src.api.v1.exam.models.exam_models import Exam
from Database.database import get_db
from src.api.v1.security import security
import os,logging
from fastapi.responses import RedirectResponse
from src.api.v1.utils.response_utils import Response

router = APIRouter()

async def get_current_user(token: str = Depends(security.JWTBearer()), db: Session = Depends(get_db)):
    """
    This helper function decodes the JWT token using decode_access_token to extract user data,
    and returns the current user.
    """
    user_data = security.decode_access_token(token)  # Decode token using the correct method
    return user_data  # Return the decoded user data to be used in the route handlers

@router.post("/exams/{exam_id}/submit/")
async def submit_exam(
    exam_id: int, 
    answers: str, 
    db: Session = Depends(get_db), 
    user_data: dict = Depends(get_current_user)
):
    """
    Submit an exam for a student
    """
    return ExamSubmissionServices.take_exam(db, exam_id, answers, user_data)

@router.put("/exams/{exam_id}/submit/{submission_id}/marks/")
async def update_marks(
    exam_id: int, 
    submission_id: int, 
    marks: float, 
    db: Session = Depends(get_db), 
    user_data: dict = Depends(get_current_user)
):
    """
    Update marks for a student's exam submission
    """
    return ExamSubmissionServices.update_marks(db, submission_id, marks, exam_id, user_data)

@router.get("/exam/{exam_id}/pdf-link")
async def get_exam_pdf_link(
    exam_id: int,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Endpoint to redirect students to the download link for the exam PDF if it's available.
    """
    try:
        result = ExamSubmissionServices.get_exam_pdf_link(db, exam_id, user_data)
        
        if isinstance(result, dict) and "download_url" in result:
            return Response(status_code=200, message="PDF download link fetched successfully.", data=result).send_success_response()
        return result
    
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")

