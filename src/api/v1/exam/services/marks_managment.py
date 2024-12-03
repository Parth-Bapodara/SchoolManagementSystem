from sqlalchemy.orm import Session
from src.api.v1.exam.models.exam_models import ExamSubmission, Exam
from src.api.v1.exam.schemas.exam_schemas import ExamSubmissionCreate, ExamSubmissionResponse
from src.api.v1.utils.response_utils import Response
from fastapi.responses import FileResponse
from botocore.exceptions import NoCredentialsError,PartialCredentialsError,ClientError
from Config.config import settings
import os,boto3,logging

class ExamSubmissionServices:

    @staticmethod
    def get_exam_pdf_link(db: Session, exam_id: int, user_data: dict):
        """
        Check if the exam has a PDF in S3 and generate a pre-signed URL for download.
        """
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        
        if not exam:
            return Response(status_code=404, message="Exam not found.", data={}).send_error_response()
        
        if not exam.exam_pdf:
            return Response(status_code=404, message="No PDF file available for this exam.", data={}).send_error_response()
        
        if exam.status != "scheduled":
            return Response(status_code=400, message="Exam is not scheduled yet.", data={}).send_error_response()

        exam_pdf_path = exam.exam_pdf
        if not exam_pdf_path:
            return Response(status_code=404, message="PDF file not found.", data={}).send_error_response()

        # Extract S3 bucket name and key
        s3_bucket = settings.AWS_S3_BUCKET_NAME
        s3_key = exam_pdf_path.replace(f"s3://{s3_bucket}/", "")

        # Create an S3 client explicitly passing credentials
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        except Exception as e:
            logging.error(f"Failed to create S3 client: {str(e)}")
            return Response(status_code=500, message="Error initializing S3 client.", data={}).send_error_response()

        try:
            # Generate a pre-signed URL to allow access to the PDF
            url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': s3_bucket, 'Key': s3_key},
                ExpiresIn=3600  # URL expires in 1 hour
            )
        except NoCredentialsError:
            logging.error("AWS credentials are missing.")
            return Response(status_code=500, message="AWS credentials error. Please check your credentials.", data={}).send_error_response()
        except PartialCredentialsError:
            logging.error("AWS credentials are incomplete.")
            return Response(status_code=500, message="Incomplete AWS credentials. Please check your configuration.", data={}).send_error_response()
        except ClientError as e:
            logging.error(f"S3 ClientError: {str(e)}")
            return Response(status_code=500, message="Error generating pre-signed URL. Check the bucket/key permissions.", data={}).send_error_response()
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            return Response(status_code=500, message="An unexpected error occurred while generating the pre-signed URL.", data={}).send_error_response()

        # Return the download URL
        return {"download_url": url}

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
