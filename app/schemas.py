from pydantic import BaseModel, Field, validator
from typing import Literal,Optional
import re
from datetime import datetime,timedelta

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

#Represents an exam's data as stored in db
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

    class Config:
        orm_mode = True

#To update exam information in the DB
class ExamUpdate(BaseModel):
    subject_id: Optional[int] = None
    class_id: Optional[int] = None
    date: Optional[datetime] = None
    duration: Optional[int] = None
    status: Optional[str] = None
    marks: Optional[float] = None

    class Config:
        orm_mode = True

#for creation of examsubmission
class ExamSubmissionCreate(BaseModel):
    answers: str

class ExamSubmissionResponse(BaseModel):
    id: int
    exam_id: int
    student_id: int
    answers: str
    marks: float

    class Config:
        orm_mode = True

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

class WeeklyReportResponse(BaseModel):
    total_hours_worked: float
    distinct_days_worked: int


class PasswordResetRequest(BaseModel):
    email: str
    reset_code: int
    new_password: str

    # Optional: validate password complexity
    @validator("new_password")
    def validate_password(cls, password):
        # Minimum password length
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        # Must contain at least one digit
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit.")
        # Must contain at least one uppercase letter
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter.")
        return password

    # Validate reset code to ensure it's a 6-digit number
    @validator("reset_code")
    def validate_reset_code(cls, code):
        if not (100000 <= code <= 999999):
            raise ValueError("Reset code must be a 6-digit number.")
        return code


class PasswordResetTokenRequest(BaseModel):
    user_id: int

#to change users password
class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=8, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_new_password: str = Field(..., min_length=8, max_length=128)

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

class Message(BaseModel):
    message:str