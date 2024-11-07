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
    email: Optional[str] = None
    password: Optional[str] = None
    username: Optional[str] = None

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

    class Config:
        orm_mode = True

#To update exam information in the DB
class ExamUpdate(BaseModel):
    subject_id: Optional[int] = None
    class_id: Optional[int] = None
    date: Optional[datetime] = None
    duration: Optional[str] = None

    class Config:
        orm_mode = True

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

#to reset user password
class PasswordResetRequest(BaseModel):
    reset_token: str
    new_password: str

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