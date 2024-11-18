from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schemas, models, database, security
from typing import List

router = APIRouter()

# Clock-in endpoint
@router.post("/clockin", response_model=schemas.AttendanceResponse)
def clock_in_user(db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    # Check if max clock-ins reached
    today_date = datetime.utcnow().date()
    today_clockins = db.query(models.Attendance).filter(
        models.Attendance.user_id == current_user.id,
        models.Attendance.clock_in >= datetime(today_date.year, today_date.month, today_date.day)
    ).count()
    
    if today_clockins >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum number of clock-ins reached for today."
        )

    attendance = models.Attendance(user_id=current_user.id, clock_in=datetime.utcnow())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    return attendance

# Clock-out endpoint
@router.post("/clockout", response_model=schemas.AttendanceResponse)
def clock_out_user(db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    # Get the latest open clock-in record
    attendance = db.query(models.Attendance).filter(
        models.Attendance.user_id == current_user.id,
        models.Attendance.clock_out == None
    ).order_by(models.Attendance.clock_in.desc()).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No open clock-in found for this user."
        )
    
    # Record clock-out time and calculate hours worked
    attendance.clock_out = datetime.utcnow()
    attendance.hours_worked = attendance.calculate_hours_worked()
    db.commit()
    db.refresh(attendance)
    
    return attendance

# Endpoint to get total work hours and distinct days worked in the last week
@router.get("/weekly-report", response_model=schemas.WeeklyReportResponse)
def get_weekly_report(db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    
    attendances = db.query(models.Attendance).filter(
        models.Attendance.user_id == current_user.id,
        models.Attendance.clock_in >= one_week_ago
    ).all()
    
    total_hours = sum(attendance.hours_worked for attendance in attendances if attendance.clock_out)
    
    worked_days = {attendance.clock_in.date() for attendance in attendances if attendance.clock_out}
    distinct_days_count = len(worked_days)
    
    return {
        "total_hours_worked": round(total_hours, 2),
        "distinct_days_worked": distinct_days_count
    }
