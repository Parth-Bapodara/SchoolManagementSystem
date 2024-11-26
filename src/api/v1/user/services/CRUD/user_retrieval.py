from fastapi import FastAPI, Depends, HTTPException, status, Request, APIRouter
from sqlalchemy.orm import Session
from src.api.v1.user.models.user_models import User
from Database.database import get_db, Base, engine
from jose import jwt, JWTError
from src.api.v1.authentication import security

router = APIRouter()

@router.get("/students/")
async def get_all_students(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    try:
        user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    if user_data["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view students, Only admin can see this Information"
        )

    students = db.query(User).filter(User.role == "student").all()
    if not students:
        return {"msg": "No students found."}

    return [{"Email": student.email, "Role": student.role, "ID": student.id, "User_name": student.username, "Status": student.status} for student in students]

# Get All Teachers (Admin-only)
@router.get("/teachers/")
async def get_all_teachers(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    try:
        user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    if user_data["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view teachers, Only admin can see this Information"
        )

    teachers = db.query(User).filter(User.role == "teacher").all()
    if not teachers:
        return {"msg": "No teachers found."}

    return [{"Email": teacher.email, "Role": teacher.role, "ID": teacher.id, "User_name": teacher.username, "Status": teacher.status} for teacher in teachers]