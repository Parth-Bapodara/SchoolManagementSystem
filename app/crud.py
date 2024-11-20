from sqlalchemy.orm import Session
from . import models
from datetime import datetime, timedelta

# Clock in user with max limit check
def clock_in_user(db: Session, user_id: int):
    # Check total clock-ins for today
    today = datetime.utcnow().date()
    clockin_count = db.query(models.Attendance).filter(
        models.Attendance.user_id == user_id,
        models.Attendance.clock_in >= datetime(today.year, today.month, today.day)
    ).count()

    if clockin_count >= 5:
        raise ValueError("Maximum clock-ins reached for today.")

    # Clock in user
    new_attendance = models.Attendance(user_id=user_id, clock_in=datetime.utcnow())
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    return new_attendance

# Clock out user and calculate hours worked
def clock_out_user(db: Session, user_id: int):
    attendance = db.query(models.Attendance).filter(
        models.Attendance.user_id == user_id,
        models.Attendance.clock_out == None
    ).first()

    if not attendance:
        raise ValueError("User is not clocked in.")

    # Set clock-out time
    attendance.clock_out = datetime.utcnow()
    attendance.hours_worked = (attendance.clock_out - attendance.clock_in).total_seconds() / 3600
    db.commit()
    db.refresh(attendance)

    # Check if user worked over 5 minutes
    if attendance.hours_worked >= 0.0833:  # 5 minutes in hours
        user = db.query(models.User).filter(models.User.id == user_id).first()
        user.attendance_count += 1
        db.commit()

    return attendance

# Get total work hours for a user
def get_total_work_hours(db: Session, user_id: int) -> str:
    attendances = db.query(models.Attendance).filter(models.Attendance.user_id == user_id).all()
    total_hours = sum(attendance.calculate_hours_worked() for attendance in attendances)

    # Format total hours for readability
    hours = int(total_hours)
    minutes = int((total_hours - hours) * 60)
    return f"{hours}h {minutes}m"

def update_exam_submission_marks(db: Session, submission_id: int, marks: float):
    submission = db.query(models.ExamSubmission).filter(models.ExamSubmission.id == submission_id).first()
    
    if submission:
        submission.marks = marks
        db.commit()
        db.refresh(submission)
        
        return submission
    return None  