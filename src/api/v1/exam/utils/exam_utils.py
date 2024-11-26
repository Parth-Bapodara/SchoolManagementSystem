from sqlalchemy.orm import Session
from src.api.v1.exam.models.exam_models import ExamSubmission
from datetime import datetime, timedelta

def update_exam_submission_marks(db: Session, submission_id: int, marks: float):
    submission = db.query(ExamSubmission).filter(ExamSubmission.id == submission_id).first()
    
    if submission:
        submission.marks = marks
        db.commit()
        db.refresh(submission)
        
        return submission
    return None  