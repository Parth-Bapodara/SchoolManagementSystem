from pydantic import BaseModel, Field, model_validator
from typing import Literal,Optional
import re
from datetime import datetime,timedelta,timezone

#For creating new diffrent Exams
class ExamCreate(BaseModel):
    subject_id: int = Field(..., example=1) 
    class_id: int = Field(..., example=1)    
    date: datetime = Field(..., example="2024-12-03T10:00:00Z")
    duration: int = Field(..., example=60) 

    class Config:
        orm_mode = True

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