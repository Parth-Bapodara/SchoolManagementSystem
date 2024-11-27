from fastapi import APIRouter, Depends
from src.api.v1.attendance.services.attendance_services import AttendanceServices
from src.api.v1.security import security
from sqlalchemy.orm import Session
from Database.database import get_db

router = APIRouter()

@router.post("/clockin")
def clock_in_user(db: Session = Depends(get_db), current_user = Depends(security.get_current_user)):
    return AttendanceServices.clock_in_user(db, current_user)

@router.post("/clockout")
def clock_out_user(db: Session = Depends(get_db), current_user = Depends(security.get_current_user)):
    return AttendanceServices.clock_out_user(db, current_user)

@router.get("/weekly-report")
def get_weekly_report(db: Session = Depends(get_db), current_user = Depends(security.get_current_user)):
    return AttendanceServices.get_weekly_report(db, current_user)
