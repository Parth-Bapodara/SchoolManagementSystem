from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, schemas, models
from .security import get_current_user
from .database import get_db
from .crud import clock_in_user,clock_out_user,get_total_work_hours

router = APIRouter()

# Clock-in endpoint
@router.post("/clockin", response_model=schemas.AttendanceResponse)
def clockin_user(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        attendance = clock_in_user(db=db, user_id=user.id)
        return attendance
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Clock-out endpoint
@router.post("/clockout", response_model=schemas.AttendanceResponse)
def clockout_user(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        attendance = clock_out_user(db=db, user_id=user.id)
        return attendance
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get total work hours endpoint
@router.get("/total_hours", response_model=str)
def get_total_work_hours(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_total_work_hours(db=db, user_id=user.id)