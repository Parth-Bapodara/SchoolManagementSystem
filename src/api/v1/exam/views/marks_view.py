from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.v1.exam.schemas.exam_schemas import ExamSubmissionCreate, ExamSubmissionResponse
from src.api.v1.exam.services.marks_managment import ExamSubmissionServices
from src.api.v1.exam.models.exam_models import Exam
from Database.database import get_db
from src.api.v1.security import security
import os
from fastapi.responses import FileResponse
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
    Endpoint for students to get a download link for the exam PDF if it's available.
    """
    try:
        result = ExamSubmissionServices.get_exam_pdf_link(db, exam_id, user_data)
        
        # If the result is a dictionary with the download URL, return it
        if isinstance(result, dict) and "download_url" in result:
            return Response(status_code=200, message="PDF download link fetched successfully.", data=result).send_success_response()
        # Handle any errors returned by `get_exam_pdf_link`
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        # Catch unexpected errors and return a 500 response
        return Response(status_code=500, message="An unexpected error occurred.", data=str(e)).send_error_response()
