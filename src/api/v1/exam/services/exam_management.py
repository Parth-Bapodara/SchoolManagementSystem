import logging,os,dateutil.parser
from datetime import datetime, timezone
from fastapi import UploadFile, File, HTTPException
from datetime import timedelta
from sqlalchemy.orm import Session
from src.api.v1.exam.utils.s3_upload import upload_file_to_s3
from src.api.v1.exam.models.exam_models import Exam
from src.api.v1.exam.models.class_subject_model import Class, Subject
from src.api.v1.exam.schemas.exam_schemas import ExamCreate,ExamUpdate
from src.api.v1.utils.response_utils import Response
from Config.config import settings

logger = logging.getLogger(__name__)

class ExamManagementServices:
    @staticmethod
    async def create_exam(db: Session, exam_data: ExamCreate, user_data: dict, exam_pdf: UploadFile = None):
        """
        Create a new exam and upload the exam PDF to S3 if provided.
        """
        if user_data["role"] != "teacher":
            return Response(status_code=403, message="Only teachers can create exams.", data={}).send_error_response()

        subject = db.query(Subject).filter(Subject.id == exam_data.subject_id).first()
        if not subject:
            return Response(status_code=404, message="Subject not found.", data={}).send_error_response()

        class_ = db.query(Class).filter(Class.id == exam_data.class_id).first()
        if not class_:
            return Response(status_code=404, message="Class not found.", data={}).send_error_response()
        
        # try:
        #     exam_date = dateutil.parser.parse(ExamCreate.date) 
        # except ValueError:
        #     return Response(status_code=400, message="Invalid date format. Use ISO 8601 format.", data={}).send_error_response()
        
        # if exam_date.tzinfo is None:
        #     exam_date = exam_date.replace(tzinfo=datetime.timezone.utc)

        exam_pdf_path = None
        if exam_pdf:
            exam_pdf_filename = f"{exam_data.subject_id}_{exam_data.class_id}_{exam_data.date.strftime('%Y%m%d%H%M%S')}.pdf"
            
            upload_successful = upload_file_to_s3(exam_pdf.file, settings.AWS_S3_BUCKET_NAME, exam_pdf_filename)

            if not upload_successful:
                return Response(status_code=500, message="Error uploading PDF file to S3.", data={}).send_error_response()

            exam_pdf_path = f"s3://{settings.AWS_S3_BUCKET_NAME}/{exam_pdf_filename}"

        new_exam = Exam(
            subject_id=exam_data.subject_id,
            class_id=exam_data.class_id,
            date=exam_data.date,
            duration=exam_data.duration,
            created_by=user_data.get("user_id"),
            exam_pdf=exam_pdf_path,
        )

        db.add(new_exam)
        db.commit()
        db.refresh(new_exam)

        return Response(
            status_code=201,
            message="Exam created successfully.",
            data={
                "exam_id": new_exam.id,
                "date": new_exam.date.isoformat(),
                "exam_pdf": exam_pdf_path if exam_pdf else None
            }
        ).send_success_response()

    @staticmethod
    def update_exam(db: Session, exam_id: int, exam_update: ExamUpdate, user_data: dict):
        """
        Update exam information
        """
        user_id = user_data.get("user_id")
        if user_data["role"] != "teacher":
            return Response(status_code=403, message="Only teachers can update exam information.", data={}).send_error_response()

        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            return Response(status_code=404, message="Exam not found.", data={}).send_error_response()

        if exam.created_by != user_id:
            return Response(status_code=403, message="You can only update exams you created.", data={}).send_error_response()

        if exam_update.subject_id:
            subject = db.query(Subject).filter(Subject.id == exam_update.subject_id).first()
            if not subject:
                return Response(status_code=404, message="Subject not found.", data={}).send_error_response()
            exam.subject_id = exam_update.subject_id

        if exam_update.class_id:
            class_ = db.query(Class).filter(Class.id == exam_update.class_id).first()
            if not class_:
                return Response(status_code=404, message="Class not found.", data={}).send_error_response()
            exam.class_id = exam_update.class_id

        if exam_update.date:
            exam_date = exam_update.date
            if exam_date.tzinfo is None:
                exam_date = exam_date.replace(tzinfo=timezone.utc)

            if exam_date < datetime.now(timezone.utc):
                return Response(status_code=400, message="Cannot create an exam with a past date or time.", data={}).send_error_response()

            exam.date = exam_date

        if exam_update.duration:
            exam.duration = exam_update.duration

        db.commit()

        updated_exam = db.query(Exam).filter(Exam.id == exam.id).first()

        return Response(
            status_code=200,
            message="Exam updated successfully.",
            data={
                "id": updated_exam.id,
                "subject_id": updated_exam.subject_id,
                "subject_name": updated_exam.subject.name,
                "class_id": updated_exam.class_id,
                "class_name": updated_exam.class_.name,
                "date": updated_exam.date.isoformat(),
                "duration": updated_exam.duration,
                "created_by": updated_exam.created_by
            }
        ).send_success_response()

    @staticmethod
    def delete_exam(db: Session, exam_id: int, user_data: dict):
        """
        Delete an exam by its ID (only if not started or finished)
        """
        user_id = user_data.get("user_id")
        if user_data["role"] not in ["admin", "teacher"]:
            return Response(status_code=403, message="Only admins or teachers can delete exams.", data={}).send_error_response()

        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            return Response(status_code=404, message="Exam not found.", data={}).send_error_response()

        if user_data["role"] == "teacher" and exam.created_by != user_id:
            return Response(status_code=403, message="You can only delete exams you created.", data={}).send_error_response()
        current_time = datetime.now(timezone.utc)

        if exam.date.tzinfo is None:
            exam_date_aware = exam.date.replace(tzinfo=timezone.utc)
        else:
            exam_date_aware = exam.date  

        exam_end_time = exam.date + timedelta(minutes=exam.duration)

        if exam.status == "scheduled" and exam_date_aware > current_time:
            db.delete(exam)
            db.commit()
            return Response(status_code=200, message="Exam deleted successfully.", data={}).send_success_response()

        return Response(status_code=400, message="You cannot delete an exam that has already started or finished.", data={}).send_error_response()

    @staticmethod
    def get_all_exams(db: Session, user_data: dict, page:int, limit:int):
        """
        Get all subjects with pagination (maximum 5 records per page).
        """
        if user_data["role"] not in ["student", "teacher"]:
            return Response(
                status_code=403, 
                message="Only students and teachers can see this information.", 
                data={}
            ).send_error_response()
        
        limit = min(limit, 5) 

        total_exams = db.query(Exam).count()
        skip = (page - 1) * limit

        exams = db.query(Exam).offset(skip).limit(limit).all()
        if not exams:
            if skip >= total_exams:
                return Response(
                    status_code=404, 
                    message="Page exceeds the number of available exams.", 
                    data={}
                ).send_error_response()
            return Response(
                status_code=404, 
                message="No exams found.", 
                data={}
            ).send_error_response()
        
        total_pages = (total_exams + limit - 1) // limit

        return Response(
            status_code=200, 
            message="Exams retrieved successfully.", 
            data={ 
                "exams": exams, 
                "total_exams": total_exams, 
                "total_pages": total_pages, 
                "page": page, 
                "limit": limit
            }
        ).send_success_response()
    

#local storage approch for storing files
# UPLOAD_DIR = "uploads/exam_papers"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

#  @staticmethod
#     async def create_exam(
#         db: Session,
#         exam_data: ExamCreate,
#         user_data: dict,
#         exam_pdf: UploadFile = None,
#     ):
#         if user_data["role"] != "teacher":
#             return Response(status_code=403, message="Only teachers can create exams.", data={}).send_error_response()
        
#         exam_date = exam_data.date
#         if exam_date.tzinfo is None:
#             exam_date = exam_date.replace(tzinfo=timezone.utc)
        
#         if exam_date < datetime.now(timezone.utc):
#             return Response(status_code=400, message="Cannot create an exam with a past date or time.", data={}).send_error_response()

#         subject = db.query(Subject).filter(Subject.id == exam_data.subject_id).first()
#         if not subject:
#             return Response(status_code=404, message="Subject not found.", data={}).send_error_response()
        
#         class_ = db.query(Class).filter(Class.id == exam_data.class_id).first()
#         if not class_:
#             return Response(status_code=404, message="Class not found.", data={}).send_error_response()

#         exam_pdf_path = None
#         if exam_pdf:
#             file_contents = await exam_pdf.read()

#             if len(file_contents) == 0:
#                 return Response(status_code=400, message="Uploaded file is empty.",data={}).send_error_response()
            
#             if len(file_contents) > MAX_FILE_SIZE:
#                 return Response(status_code=400, message="File size exceeds limit of 10MB.",data={}).send_error_response()

#             if not os.path.exists(UPLOAD_DIR):
#                 os.makedirs(UPLOAD_DIR)

#             exam_pdf_filename = f"{exam_data.subject_id}_{exam_data.class_id}_{exam_data.date.strftime('%Y%m%d%H%M%S')}.pdf"
#             exam_pdf_path = os.path.join(UPLOAD_DIR, exam_pdf_filename)

#             with open(exam_pdf_path, "wb") as f:
#                 f.write(file_contents)

#         new_exam = Exam(
#             subject_id=exam_data.subject_id,
#             class_id=exam_data.class_id,
#             date=exam_data.date,
#             duration=exam_data.duration,
#             created_by=user_data.get("user_id"),
#             exam_pdf=exam_pdf_path,
#         )

#         db.add(new_exam)
#         db.commit()
#         db.refresh(new_exam)

#         return Response (status_code=200,message= "Exam created successfully.", data={new_exam})