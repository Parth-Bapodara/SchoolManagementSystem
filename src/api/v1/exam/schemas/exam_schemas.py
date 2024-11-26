from pydantic import BaseModel, Field, validator, EmailStr, model_validator
from typing import Literal,Optional
import re
from datetime import datetime,timedelta,timezone

class ClassCreate(BaseModel):
    name:str
    
    @validator('name')
    def password_complexity(cls,value):
        if len(value) < 2:
            raise ValueError("Class name atleast contain 2 or more Characters.")
        return value

#For creating new diffrent Subjects
class SubjectCreate(BaseModel):
    name:str

    @validator('name')
    def password_complexity(cls,value):
        if len(value) < 3:
            raise ValueError("Subject name atleast contain 3 or more Characters and no Abbreviations.")
        return value

#For creating new diffrent Exams
class ExamCreate(BaseModel):
    subject_id: int
    class_id: int
    date: datetime
    duration: int

#To check if the exam is present in DB or not
class ExamInDb(BaseModel):
    id: int
    subject_id: int
    subject_name: str
    class_id: int
    class_name: str
    date: datetime 
    duration: int
    created_by: int
    status: str

    @model_validator(mode='after')  
    def ensure_utc_and_format(cls, values):
        if 'date' in values:
            date_obj = values['date']
            
            if date_obj.tzinfo is None:
                values['date'] = date_obj.replace(tzinfo=timezone.utc)
            values['date'] = values['date'].isoformat()          
        return values
    
    class Config:
        orm_mode = True

#To update exam information in the DB
class ExamUpdate(BaseModel):
    subject_id: Optional[int] = None
    class_id: Optional[int] = None
    date: Optional[datetime] = None
    duration: Optional[int] = None
    status: Optional[str] = None
    #marks: Optional[float] = None

    class Config:
        orm_mode = True

#to create new submission for exams
class ExamSubmissionCreate(BaseModel):
    answers: str

#for recording response of exam submission
class ExamSubmissionResponse(BaseModel):
    id: int
    exam_id: int
    student_id: int
    answers: str
    marks: float

    class Config:
        orm_mode = True

#for grading student marks in exmas
class ExamGrade(BaseModel):
    marks: float