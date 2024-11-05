from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .models import User, Class, Exam, Subject
from .schemas import UserCreate, UserInDb, UserUpdate, ClassCreate, SubjectCreate, ExamCreate, ExamInDb
from .database import get_db, Base, engine
from . import security
from jose import jwt, JWTError
from fastapi import APIRouter

app = FastAPI()
Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

admin_router = APIRouter(tags=["Admin Management"])
user_router = APIRouter(tags=["User Retrieval"])
exam_router = APIRouter(tags=["Exam Management"])

#for creating default admin if not available upon running system first time 
def init_db():
    db = next(get_db())
    if not db.query(User).filter(User.role == "admin").first():
        hashed_password = security.get_password_hash("DefaultAdmin@123")
        default_admin = User(
            email="admin@default.com",
            hashed_password=hashed_password,
            username="defaultAdmin",
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
    access_token = security.create_access_token(data={"sub": str(user.id), "role": user.role})
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
    
    new_subject = Class(name=subject_data.name)
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return {"msg": "Subject created successfully", "subject_id": new_subject.id}

@exam_router.post("/exams/", response_model=ExamInDb)
async def create_Exam(exam_data: ExamCreate, db:Session =Depends(get_db), token: str= Depends(oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    if user_data["role"] not in ["teacher"]:
        raise HTTPException(status_code=403, detail="Only teachers can create exams.")
    
    new_Exam = Exam(
        subject_id=exam_data.subject_id,
        class_id=exam_data.class_id,
        date=exam_data.date,
        time=exam_data.time,
        created_by=user_data["sub"]
        )
    db.add(new_Exam)
    db.commit()
    db.refresh(new_Exam)
    return new_Exam

@exam_router.get("/exama/")
async def get_exams(db:Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    if user_data["role"] != "student":
        raise HTTPException(status_code=403, detail="ONly students can view exams.")
    
    exams = db.query(Exam).all()
    return exams

app.include_router(admin_router)
app.include_router(user_router)
app.include_router(exam_router)