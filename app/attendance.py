from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from. import models, schemas, crud, database, security
from . database import SessionLocal
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

oauth2scheme= OAuth2PasswordBearer(tokenUrl="token")

#to get current logged in using JWT
def get_current_user(token:str=Depends(oauth2scheme), db: Session = Depends(SessionLocal)):
    try:
        payload=security.verify_password(token)
        user = db.query(models.User).filter(models.User.id == payload.get("user_id")).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user
    except security.JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

#logs clock-in time
@router.post("/clock-in")
async def clock_in(current_user:models.User=Depends(get_current_user), db:Session=Depends(SessionLocal)):
    existing_attendnace = db.query(models.Attendance).filter(models.Attendance.user_id == current_user.id, models.Attendance.clock_out == None).first()

    if existing_attendnace:
        raise HTTPException(status_code=400, detail="Already clocked in today")
    
    attendance = models.Attendance(user_id=current_user.id, clock_in=datetime.utcnow())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return {"message": "Clocked-in Successfully", "attendance_id": attendance.id}

#logs clock-out time
@router.post("/clock-out")
async def clock_out(current_user: models.User = Depends(get_current_user), db:Session=Depends(SessionLocal)):
    attendnace = db.query(models.Attendance).filter(models.Attendance.user_id == current_user.id, models.Attendance.clock_out == None).first()

    if not attendnace:
        raise HTTPException(status_code=400, detail="You need to clock in first")
    
    attendnace.clock_out=datetime.utcnow()
    db.commit()
    db.refresh(attendnace)

    return {"message": "Clocked-out Successfully", "attendance_id":attendnace.id}