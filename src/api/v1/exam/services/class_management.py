from fastapi import FastAPI, Depends, HTTPException, status, Request, APIRouter
from sqlalchemy.orm import Session
from src.api.v1.exam.models.exam_models import Class,Exam,Subject,ExamSubmission
from src.api.v1.exam.schemas.exam_schemas import ClassCreate, SubjectCreate, ExamCreate, ExamInDb, ExamUpdate,ExamGrade,ExamSubmissionCreate,ExamSubmissionResponse
from Database.database import get_db, Base, engine
from jose import jwt, JWTError
from src.api.v1.authentication import security

router = APIRouter()

@router.post("/classes/")
async def create_class(class_data:ClassCreate, db:Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    if user_data["role"] not in ["admin","teacher"]:
        raise HTTPException(status_code=403, detail="Only admins and teachers can create new classes.")
    
    new_class = Class(name=class_data.name)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return {"msg": "Class created successfully", "class_id": new_class.id, "name": new_class.name}

@router.get("/classes/")
async def get_all_classes(db:Session = Depends(get_db), token:str= Depends(security.oauth2_scheme)):
    try:
        user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    if user_data["role"] not in ["admin","teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and teacher can see this Information"
        )
    
    classes = db.query(Class).filter().all()
    if not classes:
        return {"msg": "No classes found."}
    
    return [{"Class-ID": class_.id, "Class_name": class_.name} for class_ in classes]

@router.post("/subjects/")
async def create_subject(subject_data: SubjectCreate, db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    if user_data["role"] not in ["admin","teacher"]:
        raise HTTPException(status_code=403, detail="Only admins and teachers can create new subjects.")
    
    new_subject = Subject(name=subject_data.name)
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return {"msg": "Subject created successfully", "subject_id": new_subject.id, "name": new_subject.name}

@router.get("/Subjects")
async def get_all_subjects(db:Session = Depends(get_db), token: str =Depends(security.oauth2_scheme)):
    try:
        user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    if user_data["role"] not in ["admin","teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and teacher can see this Information"
        )
    
    subjects = db.query(Subject).filter().all()
    if not subjects:
        return {"msg": "No subjects found."}
    
    return [{"Subject-ID": subject_.id, "Subject_name": subject_.name} for subject_ in subjects]