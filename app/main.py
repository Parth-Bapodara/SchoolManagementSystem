from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .models import User, Class, Exam, Subject
from .schemas import UserCreate, UserInDb, UserUpdate, ClassCreate, SubjectCreate, ExamCreate, ExamInDb, ExamUpdate
from .database import get_db, Base, engine
from . import security,attendance
from pydantic import EmailStr
from jose import jwt, JWTError
from fastapi import APIRouter
from . import models,schemas,database
from datetime import timedelta

app = FastAPI()
Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

admin_router = APIRouter(tags=["Admin Management"])
user_router = APIRouter(tags=["User Retrieval"])
exam_router = APIRouter(tags=["Exam Management"])
pass_router = APIRouter(tags=["Password Management"])
app.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])

#for creating default admin if not available upon running system first time 
def init_db():
    db = next(get_db())
    if not db.query(User).filter(User.role == "admin").first():
        hashed_password = security.get_password_hash("DefaultAdmin@123")
        default_admin = User(
            email="admin@default.com",
            hashed_password=hashed_password,
            username="defaultAdmin",
            passcode="admin_passcode",
            role="admin",
            status="active"
        )
        db.add(default_admin)
        db.commit()
        db.refresh(default_admin)

@app.on_event("startup")
async def startup_event():
    init_db()

# User Creation (Admin-only)
@admin_router.post("/user/create/")
async def create_user(user: UserCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    if user_data["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create new users."
        )

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists.")

    hashed_password = security.get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        username=user.username,
        status="active"  
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"msg": f"{user.role.capitalize()} created successfully", "email": db_user.email, "id": db_user.id}

# Admin and User Login
@admin_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_data = {"user_id": user.id, "role": user.role}
    access_token = security.create_access_token(data=user_data)
    # access_token = security.create_access_token(data={"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

    
# Retrieve User Info
@user_router.get("/user/me", response_model=UserInDb)
async def read_user_info(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    user_id = int(user_data.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user

# Update User Info
@user_router.put("/update-info/", response_model=UserInDb)
async def update_user_info(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    user_id = int(user_data.get("sub"))
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user_update.email:
        current_user.email = user_update.email
    if user_update.password:
        current_user.hashed_password = security.get_password_hash(user_update.password)
    if user_update.username:
        current_user.username = user_update.username

    db.commit()
    db.refresh(current_user)

    return current_user

# Get All Students (Admin-only)
@user_router.get("/students/")
async def get_all_students(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    if user_data["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view students."
        )

    students = db.query(User).filter(User.role == "student").all()
    if not students:
        return {"msg": "No students found."}

    return [{"email": student.email, "role": student.role, "ID": student.id} for student in students]

# Get All Teachers (Admin-only)
@user_router.get("/teachers/")
async def get_all_teachers(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    if user_data["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view teachers."
        )

    teachers = db.query(User).filter(User.role == "teacher").all()
    if not teachers:
        return {"msg": "No teachers found."}

    return [{"email": teacher.email, "role": teacher.role, "ID": teacher.id} for teacher in teachers]

@exam_router.post("/classes/")
async def create_class(class_data:ClassCreate, db:Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    if user_data["role"] not in ["admin","teacher"]:
        raise HTTPException(status_code=403, detail="Only admins and teachers can create new classes.")
    
    new_class = Class(name=class_data.name)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return {"msg": "Class created successfully", "class_id": new_class.id}

@exam_router.post("/subjects/")
async def create_subject(subject_data: SubjectCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    if user_data["role"] not in ["admin","teacher"]:
        raise HTTPException(status_code=403, detail="Only admins and teachers can create new subjects.")
    
    new_subject = Subject(name=subject_data.name)
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return {"msg": "Subject created successfully", "subject_id": new_subject.id}

@exam_router.post("/exams/")
async def create_Exam(exam_data: ExamCreate, db:Session =Depends(get_db), token: str= Depends(oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    if user_data["role"] not in ["teacher"]:
        raise HTTPException(status_code=403, detail="Only teachers can create exams.")
    
    subject = db.query(models.Subject).filter(models.Subject.id == exam_data.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    class_ = db.query(models.Class).filter(models.Class.id == exam_data.class_id).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    
    new_Exam = Exam(
        subject_id=exam_data.subject_id,
        class_id=exam_data.class_id,
        date=exam_data.date,
        duration=exam_data.duration,
        created_by=user_data.get("user_id")
        )
    db.add(new_Exam)
    db.commit()
    db.refresh(new_Exam)
    return new_Exam

@exam_router.get("/exams/")
async def get_exams(db:Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    if user_data["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view exams.")
    
    exams = db.query(Exam).join(Subject).join(Class).all()

    for exam in exams:
        exam.update_status()
    db.commit()

    exams_with_names = [
        {
            "id": exam.id,
            "subject_id": exam.subject_id,
            "subject_name": exam.subject.name,
            "class_id": exam.class_id,
            "class_name": exam.class_.name,
            "date": exam.date,
            "duration": exam.duration,
            "status": exam.status,
            "created_by": exam.created_by
        } 
        for exam in exams
    ]
    return exams_with_names

@exam_router.put("/exams/{exam_id}")
async def update_exam(exam_id: int, exam_update: ExamUpdate, db: Session = Depends(get_db), token:str = Depends(oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    user_id = user_data.get("user_id")
    if user_data["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can update exam information.")
    
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")

    if exam.created_by != user_id:
        raise  HTTPException(status_code=403, detail="You can only update exam info which youn created.")
    
    if exam_update.subject_id:
        subject = db.query(Subject).filter(Subject.id == exam_update.subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        exam.subject_id = exam_update.subject_id

    if exam_update.class_id:
        class_ = db.query(Class).filter(Class.id == exam_update.class_id).first()
        if not class_:
            raise HTTPException(status_code=404, detail="Subject not found")
        exam.class_id = exam_update.class_id

    if exam_update.date:
        exam.date = exam_update.date
    
    if exam_update.duration:
        exam.duration = exam_update.duration
    
    db.commit()

    updated_exam = db.query(Exam).filter(Exam.id == exam.id).first()

    return{
        "id": updated_exam.id,
        "subject_id": updated_exam.subject_id,
        "subject_name": updated_exam.subject.name,
        "class_id": updated_exam.class_id,
        "class_name": updated_exam.class_.name,
        "date": updated_exam.date,
        "duration": updated_exam.duration,
        "created_by": updated_exam.created_by
    }

@pass_router.post("/request-reset-token")
def request_reset_token(user_id: int, db: Session = Depends(get_db)):
    # Locate user by ID
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    token_data={"user_id": user.id}
    reset_token = security.create_access_token(data=token_data, expires_delta=timedelta(minutes=15))

    return{"reset_token": reset_token}

@pass_router.post("/reset-password")
def reset_password(request: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    # Decode and validate the token
    try:
        payload = security.decode_token(request.reset_token)  # Custom decode function to handle JWT decoding
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid token.")
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalid or expired.")
    
    # Find the user
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Update the user's password
    user.hashed_password = security.get_password_hash(request.new_password)
    db.commit()
    
    return {"message": "Password reset successfully."}

@pass_router.post("/change-password", response_model=schemas.Message)
def change_password(
    request: schemas.ChangePasswordRequest, 
    user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    # Verify old password
    if not security.verify_password(request.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )
    
    # Check if the new password and confirmation match
    if request.new_password != request.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation do not match"
        )

    # Hash the new password
    hashed_new_password = security.get_password_hash(request.new_password)

    # Update the password in the database
    user.hashed_password = hashed_new_password
    db.commit()

    return {"message": "Password updated successfully"}

app.include_router(admin_router)
app.include_router(user_router)
app.include_router(pass_router)
app.include_router(exam_router)