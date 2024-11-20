from pydantic import BaseModel, Field, validator, EmailStr, model_validator
from typing import Literal,Optional
import re
from datetime import datetime,timedelta,timezone

# User create Schema for user creation
class UserCreate(BaseModel):
    email: str 
    username: str 
    password: str = Field(..., min_length=8)
    role: Literal["student", "teacher", "admin"]

    @validator('password')
    def password_complexity(cls,value):
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\w).+$', value):
            raise ValueError("Password must contain an uppercase, lowercase, and atleast one special character")
        return value
    
    @validator('username')
    def username_complexity(cls,value):
        if len(value) <= 3:
            raise ValueError("Username must be at least 3 or more then characters long")
        if not re.match(r'^[a-zA-Z0-9]+$',value):
            raise ValueError("Username can only contain alphanumeric characters without spaces or special characters")
        return value
    
    @validator('email')
    def email_complexity(cls,value):
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
            raise ValueError("Invalid Email Format. Must contain '@' and valid domain.")
        return value
    
    class Config:
        schema_extra = {
            "example": {
                "email": "parth@example.com",
                "password": "Pass@1234",
                "username": "parth123",
                "role": "student"
            }
        }
        
#To check if a user is available in DB or not
class UserInDb(BaseModel):
    id: int
    hashed_password: str
    status: str = "active"
    email: str
    username: str
    role: str

    class Config:
        orm_mode = True

#To update a user information like email,username,password
class UserUpdate(BaseModel):
    password: Optional[str] = None

    @validator('password')
    def password_complexity(cls,value):
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\w).+$', value):
            raise ValueError("Password must contain an uppercase, lowercase, and atleast one special character")
        return value

#For creating new diffrent Classes 
class ClassCreate(BaseModel):
    name:str

#For creating new diffrent Subjects
class SubjectCreate(BaseModel):
    name:str

#For creating new diffrent Exams
class ExamCreate(BaseModel):
    subject_id: int
    class_id: int
    date: datetime
    duration: int

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

#to clock in user
class AttendanceIn(BaseModel):
    clock_in: datetime

#to clock out user
class AttendanceOut(BaseModel):
    clock_out: datetime

#to check attendance details
class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    clock_in: datetime
    clock_out: Optional[datetime]
    hours_worked: float

    class Config:
        orm_mode = True

#to get weekly report of users
class WeeklyReportResponse(BaseModel):
    total_hours_worked: float
    distinct_days_worked: int

#to reset user password
class PasswordResetRequest(BaseModel):
    email: EmailStr

#to verify the generated user request for password reset
class PasswordResetVerify(BaseModel):
    email: EmailStr
    code: str
    new_password: str
    confirm_password: str

    # Optional: validate password complexity
    @validator("new_password")
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit.")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter.")
        return password

#to change user password
class ChangePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

    @validator("new_password")
    def validate_password(cls, password):
        # Ensure the password is at least 8 characters, contains a digit and an uppercase letter
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit.")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter.")
        return password

class Message(BaseModel):
    message:str
