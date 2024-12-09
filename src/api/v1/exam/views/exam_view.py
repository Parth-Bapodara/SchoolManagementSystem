from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from src.api.v1.exam.schemas.exam_schemas import ExamCreate, ExamUpdate
from src.api.v1.exam.services.exam_management import ExamManagementServices
from src.api.v1.utils.response_utils import Response
from Database.database import get_db
from src.api.v1.security.security import get_logged_user
import logging,json,datetime, dateutil.parser
from typing import Dict

router = APIRouter()

@router.post("/create-exam/")
async def create_exam(
    subject_id: int = Form(...),  
    class_id: int = Form(...),
    date: str = Form(...), 
    duration: int = Form(...),
    user_data: Dict = Depends(get_logged_user), 
    exam_pdf: UploadFile = File(None),  
    db: Session = Depends(get_db) 
):
    try:
       
        try:
            exam_date = dateutil.parser.parse(date) 
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use ISO 8601 format.")
        
        if exam_date.tzinfo is None:
            exam_date = exam_date.replace(tzinfo=datetime.timezone.utc)

        exam_data_parsed = ExamCreate(
            subject_id=subject_id,
            class_id=class_id,
            date=exam_date,
            duration=duration
        )
        return await ExamManagementServices.create_exam(
            exam_data=exam_data_parsed,
            db=db,
            user_data=user_data,
            exam_pdf=exam_pdf
        )

    except Exception as e:
        return Response(status_code=500, message=str(e), data={}).send_error_response()

@router.get("/exams/")
async def get_all_exams(
    db: Session = Depends(get_db), 
    user_data: dict = Depends(get_logged_user),
    page: int = 1,
    limit: int = 5
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
    user_data: dict = Depends(get_logged_user)
):
    """
    Update an existing exam
    """
    return ExamManagementServices.update_exam(db, exam_id, exam_update, user_data)

@router.delete("/exams/{exam_id}")
async def delete_exam(
    exam_id: int, 
    db: Session = Depends(get_db), 
    user_data: dict = Depends(get_logged_user)
):
    """
    Delete an exam by ID
    """
    return ExamManagementServices.delete_exam(db, exam_id, user_data)


# Storing files in local storage
# @router.post("/create-exam/")
# async def create_exam(
#     exam_data: str = Form(...),  # Accepting exam data as a JSON string in the form field
#     user_data: dict = Depends(get_current_user),  # Extract current user from JWT token
#     exam_pdf: UploadFile = File(None),  # Optional file upload
#     db: Session = Depends(get_db)  # Database session dependency
# ):
#     try:
#         try:
#             exam_dict = json.loads(exam_data)  
#         except json.JSONDecodeError:
#             raise HTTPException(status_code=400, detail="Invalid JSON format in exam data.")
        
#         try:
#             exam_date = dateutil.parser.parse(exam_dict['date'])
#         except ValueError:
#             raise HTTPException(status_code=400, detail="Invalid date format. Use ISO 8601 format.")
        
#         if exam_date.tzinfo is None:
#             exam_date = exam_date.replace(tzinfo=datetime.timezone.utc)

#         exam_data_parsed = ExamCreate(
#             subject_id=exam_dict['subject_id'],
#             class_id=exam_dict['class_id'],
#             date=exam_date,
#             duration=exam_dict['duration']
#         )

#         return await ExamManagementServices.create_exam(
#             exam_data=exam_data_parsed,
#             db=db,
#             user_data=user_data,
#             exam_pdf=exam_pdf
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
