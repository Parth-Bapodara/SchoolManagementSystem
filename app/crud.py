from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timedelta

def clock_in_user(db: Session, user_id: int):
    attendance = models.Attendance(user_id=user_id, clock_in=datetime.utcnow())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance

def clock_out_user(db: Session, user_id: int):
    attendance = db.query(models.Attendance).filter(models.Attendance.user_id == user_id, models.Attendance.clock_out == None).first()
    
    if not attendance:
        return None

    attendance.clock_out = datetime.utcnow()
    db.commit()
    db.refresh(attendance)
    return attendance

def get_total_work_hours(db:Session, user_id:int):
    attendances = db.query(models.Attendance).filter(models.Attendance.user_id).all()
    total_hours = sum(attendance.hours_worked for attendance in attendances)
    return total_hours

    # for attendance in attendances:
    #     if attendance.clock_out:
    #         total_hours += (attendance.clock_out - attendance.clock_in)

    # return total_hours.total_seconds()/3600