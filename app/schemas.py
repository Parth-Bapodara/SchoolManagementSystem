from pydantic import BaseModel, Field, validator
import re

class UserCreate(BaseModel):
    email: str
    password: str = Field(..., min_length=8)
    role: str = Field("student")

    @validator('password')
    def password_complexity(cls,value):
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\w).+$', value):
            raise ValueError("Password must contain an uppercase, lowercase, and atleast one special character")
        return value

class UserInDb(UserCreate):
    hashed_password: str


# class AdminCreate(BaseModel):
#     username: str
#     email: str
#     password: str

# class AdminResponse(BaseModel):
#     id: int
#     username: str
#     email: str
#     access_token: str
#     token_type: str

#     class Config:
#         orm_mode = True

# class StudentCreate(BaseModel):
#     username: str
#     email: str
#     password: str

# class StudentResponse(BaseModel):
#     id: int
#     username: str
#     email: str

#     class Config:
#         orm_mode = True

# class TeacherCreate(BaseModel):
#     username: str
#     email: str
#     password: str

# class TeacherResponse(BaseModel):
#     id: int
#     username: str
#     email: str

#     class Config:
#         orm_mode = True

