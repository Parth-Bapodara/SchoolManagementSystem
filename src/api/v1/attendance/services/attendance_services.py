from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.v1.authentication import security
from src.api.v1.user.models.user_models import User
from src.api.v1.attendance.models.attendance_models import Attendance
from src.api.v1.attendance.schemas.attendance_schemas import AttendanceIn,AttendanceOut,AttendanceResponse,WeeklyReportResponse
from Database import database
from typing import List

router = APIRouter()

# Clock-in endpoint
@router.post("/clockin", response_model=AttendanceResponse)
def clock_in_user(db: Session = Depends(database.get_db), current_user: User = Depends(security.get_current_user)):
    today_date = datetime.utcnow().date()
    today_clockins = db.query(Attendance).filter(
        Attendance.user_id == current_user.id,
        Attendance.clock_in >= datetime(today_date.year, today_date.month, today_date.day)
    ).count()
    
    if today_clockins >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum number of clock-ins reached for today."
        )

    attendance = Attendance(user_id=current_user.id, clock_in=datetime.utcnow())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    return attendance

# Clock-out endpoint
@router.post("/clockout", response_model=AttendanceResponse)
def clock_out_user(db: Session = Depends(database.get_db), current_user: User = Depends(security.get_current_user)):
    attendance = db.query(Attendance).filter(
        Attendance.user_id == current_user.id,
        Attendance.clock_out == None
    ).order_by(Attendance.clock_in.desc()).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No open clock-in found for this user."
        )
    
    attendance.clock_out = datetime.utcnow()
    attendance.hours_worked = attendance.calculate_hours_worked()
    db.commit()
    db.refresh(attendance)
    
    return attendance

# Endpoint to get total work hours and distinct days worked in the last week
@router.get("/weekly-report", response_model=WeeklyReportResponse)
def get_weekly_report(db: Session = Depends(database.get_db), current_user: User = Depends(security.get_current_user)):
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    
    attendances = db.query(Attendance).filter(
        Attendance.user_id == current_user.id,
        Attendance.clock_in >= one_week_ago
    ).all()
    
    total_hours = sum(attendance.hours_worked for attendance in attendances if attendance.clock_out)
    
    worked_days = {attendance.clock_in.date() for attendance in attendances if attendance.clock_out}
    distinct_days_count = len(worked_days)
    
    return {
        "total_hours_worked": round(total_hours, 2),
        "distinct_days_worked": distinct_days_count
    }
