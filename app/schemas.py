from pydantic import BaseModel, Field, EmailStr

class AdminSchema(BaseModel):
    f_name: str = Field(...)
    l_name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "f_name" : "Parth",
                "l_name" : "Bapodara",
                "email" : "demo@gmail.com",
                "password" : "weakpassword"
            }
        }

class AdminLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "demo@gmail.com",
                "password": "weakpassword"
            }
        }

class UserSchema(BaseModel):
    f_name: str = Field(...)
    l_name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    role: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "f_name" : "Parth",
                "l_name" : "Bapodara",
                "email" : "demo@gmail.com",
                "password" : "weakpassword",
                "role" : "Teacher or Student"   
            }
        }
    
class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "demo@gmail.com",
                "password": "weakpassword"
            }
        }