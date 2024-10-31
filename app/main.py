from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .models import User
from .schemas import UserCreate
from .database import get_db, Base, engine
from . import security

app = FastAPI()
Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")

# Admin Registration
@app.post("/admin/register/")
async def register_admin(user: UserCreate, db: Session = Depends(get_db)):
    existing_admin = db.query(User).filter(User.role == "admin").first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An admin user already exists."
        )
    
    hashed_password = security.get_password_hash(user.password)
    db_admin = User(email=user.email, hashed_password=hashed_password, role="admin")
    
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    
    return {"msg": "Admin user created successfully", "email": db_admin.email}

# Admin Login
@app.post("/admin/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

# Add Teacher
@app.post("/teachers/")
async def create_teacher(user: UserCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    if user_data["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add teachers"
        )
    
    hashed_password = security.hash_password(user.password)
    db_teacher = User(email=user.email, hashed_password=hashed_password, role="teacher")
    
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    
    return {"msg": "Teacher added successfully", "email": db_teacher.email}

# Add Student
@app.post("/students/")
async def create_student(user: UserCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    if user_data["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add students"
        )
    
    hashed_password = security.hash_password(user.password)
    db_student = User(email=user.email, hashed_password=hashed_password, role="student")
    
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    
    return {"msg": "Student added successfully", "email": db_student.email}

# Get Teacher by ID
@app.get("/teachers/{email}")
async def get_teacher(email: str, db: Session = Depends(get_db)):
    teacher = db.query(User).filter(User.email == email, User.role == "teacher").first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    return {"email": teacher.email, "role": teacher.role}

# Get Student by ID
@app.get("/students/{email}")
async def get_student(email: str, db: Session = Depends(get_db)):
    student = db.query(User).filter(User.email == email, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {"email": student.email, "role": student.role}

# Get All Teachers
@app.get("/teachers/")
async def get_all_teachers(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    if user_data["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view teachers"
        )
    
    teachers = db.query(User).filter(User.role == "teacher").all()
    return [{"email": teacher.email, "role": teacher.role} for teacher in teachers]

# Get All Students
@app.get("/students/")
async def get_all_students(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    if user_data["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view students"
        )
    
    students = db.query(User).filter(User.role == "student").all()
    return [{"email": student.email, "role": student.role} for student in students]



# @app.post("/admin/register", response_model=schemas.AdminResponse, tags=["admin"])
# def register(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
#     db_admin = db.query(models.Admin).filter(models.Admin.username == admin.username).first()
#     if db_admin:
#         raise HTTPException(status_code=400, detail="Username already registered")

#     if not validate_password(admin.password):
#         raise HTTPException(status_code=400, detail="Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, and a special character")

#     hashed_password = get_password_hash(admin.password)
#     new_admin = models.Admin(username=admin.username, email=admin.email, hashed_password=hashed_password)
#     db.add(new_admin)
#     db.commit()
#     db.refresh(new_admin)

#     access_token = create_access_token(data={"sub": new_admin.username})
#     return schemas.AdminResponse(
#         id=new_admin.id,
#         username=new_admin.username,
#         email=new_admin.email,
#         access_token=access_token,
#         token_type="bearer"
#     )

# # def authorize_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
  
# #     payload = auth.decode_access_token(token)
# #     if payload.get("role") != "admin":
# #         raise HTTPException(
# #             status_code=status.HTTP_403_FORBIDDEN,
# #             detail="Admin authorization required"
# #         )
# #     return payload

# @app.post("/add_teacher", response_model=schemas.TeacherResponse, tags=["admin"])
# def add_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db),current_user:models.Admin = Depends(get_current_user)):
#     db_teacher = db.query(models.Teacher).filter(models.Teacher.username == teacher.username).first()
#     if db_teacher:
#         raise HTTPException(status_code=400, detail="Teacher already registered")

#     if not validate_password(teacher.password):
#         raise HTTPException(status_code=400, detail="Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, and a special character")

#     hashed_password = get_password_hash(teacher.password)
#     new_teacher = models.Teacher(username=teacher.username, email=teacher.email, hashed_password=hashed_password)
#     db.add(new_teacher)
#     db.commit()
#     db.refresh(new_teacher)

#     return new_teacher

# @app.post("/add_student", response_model=schemas.StudentResponse, tags=["admin"])
# def add_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
#     db_student = db.query(models.Student).filter(models.Student.username == student.username).first()
#     if db_student:
#         raise HTTPException(status_code=400, detail="Student already registered")

#     if not validate_password(student.password):
#         raise HTTPException(status_code=400, detail="Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, and a special character")

#     hashed_password = get_password_hash(student.password)
#     new_student = models.Student(username=student.username, email=student.email, hashed_password=hashed_password)
#     db.add(new_student)
#     db.commit()
#     db.refresh(new_student)

#     return new_student

# def validate_password(password: str) -> bool:
#     import re
#     # Check if the password meets the requirements
#     return (len(password) >= 8 and
#             re.search(r"[A-Z]", password) and
#             re.search(r"[a-z]", password) and
#             re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

