from sqlalchemy.orm import Session
from src.api.v1.exam.models.exam_models import ExamSubmission, Exam
from src.api.v1.exam.schemas.exam_schemas import ExamSubmissionCreate, ExamSubmissionResponse
from src.api.v1.utils.response_utils import Response

class ExamSubmissionServices:

    @staticmethod
    def take_exam(db: Session, exam_id: int, answers: str, user_data: dict):
        """
        Submit an exam for a student
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
