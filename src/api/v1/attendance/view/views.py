from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.api.v1.attendance.services.attendance_services import AttendanceServices
from Database.database import get_db
from src.api.v1.security.security import get_current_user  # Use the new function
from src.api.v1.user.models.user_models import User

router = APIRouter()

@router.post("/clock-in")
def clock_in(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AttendanceServices.clock_in_user(db=db, current_user=current_user)

@router.post("/clock-out")
def clock_out(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AttendanceServices.clock_out_user(db=db, current_user=current_user)

@router.get("/weekly-report")
def weekly_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AttendanceServices.get_weekly_report(db=db, current_user=current_user)
