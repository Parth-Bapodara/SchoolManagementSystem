from sqlalchemy.orm import Session
from src.api.v1.user.models.user_models import User
from src.api.v1.exam.models.exam_models import ExamSubmission, Exam
from src.api.v1.exam.schemas.exam_schemas import ExamSubmissionCreate, ExamSubmissionResponse
from src.api.v1.utils.response_utils import Response
from fastapi.responses import FileResponse
from fastapi.exceptions import HTTPException
from botocore.exceptions import NoCredentialsError,PartialCredentialsError,ClientError
from Config.config import settings
import os,boto3,logging

class ExamSubmissionServices:

    @staticmethod
    def get_exam_pdf_link(db: Session, exam_id: int, user_data: dict):
        """
        Check if the exam has a PDF in S3 and generate a pre-signed URL for download.
        """
        # Fetch the exam from the database
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found.")
        
        # Ensure the exam is in a scheduled state
        if exam.status != "scheduled":
            raise HTTPException(status_code=400, detail="Exam is not scheduled yet.")

        # Check if the exam has a PDF available
        if not exam.exam_pdf:
            raise HTTPException(status_code=404, detail="No PDF file available for this exam.")
        
        # Extract the S3 bucket and key
        s3_bucket = settings.AWS_S3_BUCKET_NAME
        s3_key = exam.exam_pdf.replace(f"s3://{s3_bucket}/", "")
        
        try:
            # Create S3 client
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            s3.head_object(Bucket=s3_bucket, Key=s3_key)

        except ClientError as e:
            logging.error(f"Error accessing the file in S3: {str(e)}")
            raise HTTPException(status_code=404, detail="PDF not found in S3.")
        
        try:
            url = s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': s3_bucket,
                    'Key': s3_key,
                    'ResponseContentDisposition': 'inline',  
                    'ResponseContentType': 'application/pdf',  
                },
                ExpiresIn=3600 
            )
            return {"download_url": url}
        
        except Exception as e:
            logging.error(f"Error generating pre-signed URL: {str(e)}")
            raise HTTPException(status_code=500, detail="Error generating pre-signed URL.")

    @staticmethod
    def take_exam(db: Session, exam_id: int, answers: str, user_data: dict):
        """
        Submit an exam for a student and check for PDF availability on S3.
        """
        if user_data["role"] != "student":
            return Response(status_code=403, message="Only students can take exams.", data={}).send_error_response()

        exam = db.query(Exam).filter(Exam.id == exam_id, Exam.status == "scheduled").first()
        if not exam:
            return Response(status_code=404, message="Exam not available or already started/completed.", data={}).send_error_response()

        existing_submission = db.query(ExamSubmission).filter(ExamSubmission.exam_id == exam_id, ExamSubmission.student_id == user_data["user_id"]).first()
        if existing_submission:
            return Response(status_code=400, message="You have already submitted this exam.", data={}).send_error_response()

        submission = ExamSubmission(exam_id=exam_id, student_id=user_data["user_id"], answers=answers)
        db.add(submission)
        db.commit()
        db.refresh(submission)

        if exam.exam_pdf:
            pdf_response = ExamSubmissionServices.get_exam_pdf_link(db, exam_id, user_data)
            return pdf_response  

        return Response(
            status_code=201,
            message="Exam submitted successfully.",
            data={"submission_id": submission.id}
        ).send_success_response()

    @staticmethod
    def update_marks(db: Session, submission_id: int, marks: float, exam_id: int, user_data: dict):
        """
        Update marks for a student's exam submission
        """
        if user_data["role"] != "teacher":
            return Response(status_code=403, message="Only teachers can update marks.", data={}).send_error_response()

        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            return Response(status_code=404, message="Exam not found.", data={}).send_error_response()

        submission = db.query(ExamSubmission).filter(ExamSubmission.id == submission_id, ExamSubmission.exam_id == exam_id).first()
        if not submission:
            return Response(status_code=404, message="Submission not found.", data={}).send_error_response()

        submission.marks = marks
        db.commit()

        return Response(
            status_code=200,
            message="Marks updated successfully.",
            data={"submission_id": submission.id, "marks": submission.marks}
        ).send_success_response()
