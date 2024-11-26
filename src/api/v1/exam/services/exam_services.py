from fastapi import FastAPI, Depends, HTTPException, status, Request, APIRouter
from sqlalchemy.orm import Session
from src.api.v1.exam.models.exam_models import Class,Exam,Subject,ExamSubmission
from src.api.v1.exam.schemas.exam_schemas import ClassCreate, SubjectCreate, ExamCreate, ExamInDb, ExamUpdate,ExamGrade,ExamSubmissionCreate,ExamSubmissionResponse
from src.api.v1.authentication import security
from datetime import timedelta, datetime, timezone
from Database.database import get_db
from jose import jwt,JWTError
from src.api.v1.exam.utils.exam_utils import update_exam_submission_marks

router = APIRouter()

@router.post("/exams/")
async def create_Exam(exam_data: ExamCreate, db:Session =Depends(get_db), token: str= Depends(security.oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    if user_data["role"] not in ["teacher"]:
        raise HTTPException(status_code=403, detail="Only teachers can create exams.")
    
    exam_date = exam_data.date

    if exam_date.tzinfo is None:
        exam_date = exam_date.replace(tzinfo=timezone.utc)
    
    if exam_date<datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Cannot create an exam with a past date or time.")

    subject = db.query(Subject).filter(Subject.id == exam_data.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    class_ = db.query(Class).filter(Class.id == exam_data.class_id).first()
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

@router.get("/exams/")
async def get_exams(db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    if user_data["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view exams.")
    
    exams = db.query(Exam).join(Subject).join(Class).all()
    current_time = datetime.now(timezone.utc)

    for exam in exams:
        if exam.date.tzinfo is None:
            exam.date = exam.date.replace(tzinfo=timezone.utc)  
        
        exam_end_time = exam.date + timedelta(minutes=exam.duration)

        if exam_end_time <= current_time and exam.status == "scheduled":
            exam.status = "finished"
            db.commit()

    exams_with_names = [
        {
            "id": exam.id,
            "subject_id": exam.subject_id,
            "subject_name": exam.subject.name,
            "class_id": exam.class_id,
            "class_name": exam.class_.name,
            "date": exam.date.isoformat(), 
            "duration": exam.duration,
            "status": exam.status,
            "created_by": exam.created_by
        }
        for exam in exams
    ]
    return exams_with_names

@router.put("/exams/{exam_id}")
async def update_exam(exam_id: int, exam_update: ExamUpdate, db: Session = Depends(get_db), token:str = Depends(security.oauth2_scheme)):
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
            raise HTTPException(status_code=404, detail="Class not found")
        exam.class_id = exam_update.class_id

    if exam_update.date:
        exam_date = exam_update.date
        if exam_date.tzinfo is None:
            exam_date = exam_date.replace(tzinfo=timezone.utc)
    
        if exam_date<datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Cannot create an exam with a past date or time.")
        
        exam.date=exam_date
    
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

@router.post("/exams/{exam_id}/take")
async def take_exam(exam_id: int, answers: str, db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    try:
        # Decode and verify the user's role
        user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")

    if user_data["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can take exams.")
    
    exam = db.query(Exam).filter(Exam.id == exam_id, Exam.status == "scheduled").first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not available or already started/completed.")

    existing_submission = db.query(ExamSubmission).filter(ExamSubmission.exam_id == exam_id, ExamSubmission.student_id == user_data["user_id"]).first()
    if existing_submission:
        raise HTTPException(status_code=400, detail="You have already submitted this exam.")

    submission = ExamSubmission(exam_id=exam_id, student_id=user_data["user_id"], answers=answers)
    db.add(submission)
    db.commit()
    db.refresh(submission)  
    
    return {
        "message": "Exam submitted successfully.",
        "submission_id": submission.id
    }

@router.put("/exam-submissions/{submission_id}/marks", response_model=ExamSubmissionResponse)
async def update_marks(submission_id: int, marks: float, exam_id: int, db: Session = Depends(get_db), token: str = Depends(security.oauth2_scheme)):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    
    if user_data["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can update/give marks.")
    
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")
    
    if exam.status != "finished":
        raise HTTPException(status_code=400, detail="Marks can only be entered after the completion of the exam.")
    
    submission = update_exam_submission_marks(db, submission_id, marks)
    
    if submission:
        return ExamSubmissionResponse(
            id=submission.id,
            exam_id=submission.exam_id,
            student_id=submission.student_id,
            answers=submission.answers,
            marks=submission.marks
        )
    else:
        raise HTTPException(status_code=404, detail="Exam Submission not found.")    
    
@router.get("/exams/{exam_id}/marks")
async def get_exam_marks(
    exam_id: int, 
    db: Session = Depends(get_db), 
    token: str = Depends(security.oauth2_scheme)
):
    user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])

    student_id = None
    if user_data["role"] == "student":
        student_id = user_data["user_id"]
    elif user_data["role"] == "teacher":
        student_id = None  
    else:
        raise HTTPException(status_code=403, detail="Unauthorized access.")
    
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found.")
    
    if student_id:
        submission = db.query(ExamSubmission).filter(
            ExamSubmission.exam_id == exam_id,
            ExamSubmission.student_id == student_id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="No submission found for this student.")
        
        return {"exam_id": exam_id, "marks": submission.marks}
    
    submissions = db.query(ExamSubmission).filter(ExamSubmission.exam_id == exam_id).all()
    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found for this exam.")
    
    return [
        {"student_id": submission.student_id, "marks": submission.marks}
        for submission in submissions
    ]