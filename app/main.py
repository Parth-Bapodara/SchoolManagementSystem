from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .models import User
from .schemas import UserCreate, UserInDb
from .database import get_db, Base, engine
from . import security
from jose import jwt
from fastapi import APIRouter
from . import database,models,schemas,database

app = FastAPI()
Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

admin_router = APIRouter(tags=["Admin Management"])
user_router = APIRouter(tags=["User Retrieval"])

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
@admin_router.post("/user/create/", response_model=UserInDb)
async def create_user(user: UserCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    
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

# Admin Login
@admin_router.post("/login")
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

@admin_router.get("/user/{user_id}", response_model=schemas.UserInDb)
async def read_user_info(user_id: int, db:Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found")
    return user

# Get All Students (Admin-only)
@user_router.get("/students/")
async def get_all_students(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
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
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    if user_data["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view students."
        )
    
    teachers = db.query(User).filter(User.role == "teacher").all()
    if not teachers:
        return {"msg": "No Teachers found."}
    
    return [{"email": teacher.email, "role": teacher.role, "ID": teacher.id} for teacher in teachers]

@user_router.get("/users/{user_id}")
async def get_user_by_id(user_id:int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return{"id": user.id, "email": user.email, "role": user.role, "status": user.status}




app.include_router(admin_router)
app.include_router(user_router)