from sqlalchemy.orm import Session
from src.api.v1.exam.models.exam_models import Exam
from src.api.v1.exam.models.class_subject_model import Class, Subject
from src.api.v1.exam.schemas.exam_schemas import ExamCreate, ExamUpdate
from src.api.v1.security import security
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from src.api.v1.utils.response_utils import Response
import logging
from fastapi import UploadFile, File

logger = logging.getLogger(__name__)

class ExamManagementServices:

    @staticmethod
    def create_exam(db: Session, exam_data: ExamCreate, user_data: dict, exam_pdf: UploadFile = File(None)):
        """
        Create a new exam with optional exam PDF upload.
        """
        if user_data["role"] != "teacher":
            return Response(status_code=403, message="Only teachers can create exams.", data={}).send_error_response()
        
        exam_date = exam_data.date
        if exam_date.tzinfo is None:
            exam_date = exam_date.replace(tzinfo=timezone.utc)

        if exam_date < datetime.now(timezone.utc):
            return Response(status_code=400, message="Cannot create an exam with a past date or time.", data={}).send_error_response()

        subject = db.query(Subject).filter(Subject.id == exam_data.subject_id).first()
        if not subject:
            return Response(status_code=404, message="Subject not found.", data={}).send_error_response()

        class_ = db.query(Class).filter(Class.id == exam_data.class_id).first()
        if not class_:
            return Response(status_code=404, message="Class not found.", data={}).send_error_response()

        # Save the exam PDF if provided
        exam_pdf_path = None
        if exam_pdf:
            # Save the file to the server (ensure this directory exists)
            exam_pdf_path = f"uploaded_files/exams/{exam_pdf.filename}"
            with open(exam_pdf_path, "wb") as f:
                f.write(exam_pdf.file.read())

        new_exam = Exam(
            subject_id=exam_data.subject_id,
            class_id=exam_data.class_id,
            date=exam_data.date,
            duration=exam_data.duration,
            created_by=user_data.get("user_id"),
            exam_pdf=exam_pdf_path  # Save the file path in the database
        )

        db.add(new_exam)
        db.commit()
        db.refresh(new_exam)

        return Response(
            status_code=201, 
            message="Exam created successfully.", 
            data={"exam_id": new_exam.id, "date": new_exam.date.isoformat(), "exam_pdf": exam_pdf_path}
        ).send_success_response()

    @staticmethod
    def get_all_exams(db: Session, user_data: dict, page: int, limit: int):
        """
        Get all exams with pagination
        """
        if user_data["role"] != "student":
            return Response(status_code=403, message="Only students can view exams.", data={}).send_error_response()
        
        total_exams = db.query(Exam).count()
        skip = (page - 1) * limit

        exams = db.query(Exam).join(Subject).join(Class).offset(skip).limit(limit).all()
        current_time = datetime.now(timezone.utc)

        for exam in exams:
            if exam.date.tzinfo is None:
                exam.date = exam.date.replace(tzinfo=timezone.utc)

            exam_end_time = exam.date + timedelta(minutes=exam.duration)
            if exam_end_time <= current_time and exam.status == "scheduled":
                exam.status = "finished"
                db.commit()

        exams_with_names = [
            {
                "id": exam.id,
                "subject_id": exam.subject_id,
                "subject_name": exam.subject.name,
                "class_id": exam.class_id,
                "class_name": exam.class_.name,
                "date": exam.date.isoformat(),
                "duration": exam.duration,
                "status": exam.status,
                "created_by": exam.created_by
            }
            for exam in exams
        ]
        total_pages = (total_exams + limit - 1) // limit

        return Response(
            status_code=200,
            message="Exams retrieved successfully.",
            data={
                "exams": exams_with_names,
                "total_exams": total_exams,
                "total_pages": total_pages,
                "page": page,
                "limit": limit
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
