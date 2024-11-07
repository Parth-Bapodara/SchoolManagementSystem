from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models, schemas, crud, database
from .security import get_current_user

router = APIRouter()

MAX_CLOCK_INS = 5  # Limit for clock-ins

@router.post("/clock-in")
def clock_in(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    # Check if user can clock in (max clock-ins not reached)
    user_clock_ins = db.query(models.Attendance).filter(models.Attendance.user_id == current_user.id).count()

    if user_clock_ins >= MAX_CLOCK_INS:
        raise HTTPException(status_code=400, detail=f"You have reached the maximum of {MAX_CLOCK_INS} clock-ins.")
    
    # Find the latest attendance record for the user
    latest_attendance = db.query(models.Attendance).filter(models.Attendance.user_id == current_user.id).order_by(models.Attendance.clock_in.desc()).first()

    if latest_attendance and latest_attendance.clock_out is None:
        raise HTTPException(status_code=400, detail="You are already clocked in.")

    # Create a new attendance record for the user with current time as clock-in
    new_attendance = models.Attendance(user_id=current_user.id, clock_in=datetime.utcnow())
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    
    return {"message": "Clocked in successfully", "attendance_id": new_attendance.id}

@router.post("/clock-out")
def clock_out(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    # Find the latest attendance record for the user
    latest_attendance = db.query(models.Attendance).filter(models.Attendance.user_id == current_user.id).order_by(models.Attendance.clock_in.desc()).first()

    if not latest_attendance or latest_attendance.clock_out:
        raise HTTPException(status_code=400, detail="You are not clocked in.")
    
    # Automatically set clock-out time to current time
    latest_attendance.clock_out = datetime.utcnow()
    latest_attendance.hours_worked = latest_attendance.calculate_hours_worked()

    # If the user worked more than 5 minutes, increment the attendance count (if required)
    if latest_attendance.hours_worked >= 0.0833:  # 5 minutes = 0.0833 hours
        pass

    db.commit()
    db.refresh(latest_attendance)

    return {"message": "Clocked out successfully", "hours_worked": round(latest_attendance.hours_worked, 2)}

@router.get("/total-hours/{user_id}")
def total_hours(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    total_hours = sum(attendance.hours_worked for attendance in user.attendances)
    
    return {"total_hours": round(total_hours, 2)}