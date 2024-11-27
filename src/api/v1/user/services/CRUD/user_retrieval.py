from fastapi import FastAPI, Depends, HTTPException, status, Request, APIRouter
from sqlalchemy.orm import Session
from src.api.v1.user.models.user_models import User
from Database.database import get_db
from jose import jwt, JWTError
from src.api.v1.security import security
from src.api.v1.utils.response_utils import Response

router = APIRouter()

DEFAULT_PAGE = 1
DEFAULT_LIMIT = 5

def get_skip_and_limit(page: int, limit: int):
    skip = (page - 1) * limit
    return skip, limit

@router.get("/admins/")
async def get_admins(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme),
                           page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT):
    try:
        user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    except JWTError:
        return Response(status_code=403, message="Could not validate credentials", data={}).send_error_response()

    if user_data["role"] != "admin":
        return Response(
            status_code=403,
            message="Not authorized to view admins, Only other admin can see this Information",
            data={}
        ).send_error_response()
    
    skip, limit = get_skip_and_limit(page, limit)

    admins = db.query(User).filter(User.role == "admin").offset(skip).limit(limit).all()
    if not admins:
        return {"msg": "No admins found."}

    return {
        "page": page,
        "limit": limit,
        "students": [{"Email": admin.email, "Role": admin.role, "ID": admin.id, "User_name": admin.username, "Status": admin.status} for admin in admins]
    }

@router.get("/students/")
async def get_students(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme),
                           page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT):
    try:
        user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    except JWTError:
        return Response(status_code=403, message="Could not validate credentials", data={}).send_error_response()

    if user_data["role"] != "admin":
        return Response(
            status_code=403,
            message="Not authorized to view students, Only admin can see this Information",
            data={}
        ).send_error_response()
    
    skip, limit = get_skip_and_limit(page, limit)

    students = db.query(User).filter(User.role == "student").offset(skip).limit(limit).all()
    if not students:
        return {"msg": "No students found."}

    return {
        "page": page,
        "limit": limit,
        "students": [{"Email": student.email, "Role": student.role, "ID": student.id, "User_name": student.username, "Status": student.status} for student in students]
    }

@router.get("/teachers/")
async def get_teachers(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme),
                            page: int = DEFAULT_PAGE, limit: int = DEFAULT_LIMIT):
    try:
        user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    except JWTError:
        return Response(status_code=403, message="Could not validate credentials", data={}).send_error_response()

    if user_data["role"] != "admin":
        return Response(
            status_code=403,
            message="Not authorized to view teachers, Only admin can see this Information",
            data={}
        ).send_error_response()

    skip, limit = get_skip_and_limit(page, limit)

    teachers = db.query(User).filter(User.role == "teacher").offset(skip).limit(limit).all()
    if not teachers:
        return {"msg": "No teachers found."}

    return {
        "page": page,
        "limit": limit,
        "teachers": [{"Email": teacher.email, "Role": teacher.role, "ID": teacher.id, "User_name": teacher.username, "Status": teacher.status} for teacher in teachers]
    }
