from pydantic import BaseModel, Field, validator, EmailStr, model_validator
from typing import Literal,Optional
import re
from datetime import datetime,timedelta,timezone

# User create Schema for user creation
class UserCreate(BaseModel):
    email: str 
    username: str 
    password: str = Field(...)
    role: Literal["student", "teacher", "admin"]

    @validator('password')
    def password_complexity(cls,value):
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\w).+$', value):
            raise ValueError("Password must contain an uppercase, lowercase, and atleast one special character ")
        if len(value) < 8:
            raise ValueError("Password should be minimum of 8 Characters.")
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
    def password_complexity(cls, value):
        if value and not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).+$', value):
            raise ValueError("Password must contain an uppercase, lowercase, at least one digit, and at least one special character.")
        if value and len(value) < 8:
            raise ValueError("Password should be a minimum of 8 characters.")
        return value