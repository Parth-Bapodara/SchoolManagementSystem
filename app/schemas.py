from pydantic import BaseModel, Field, EmailStr, validator

class UserSchema(BaseModel):
    f_name: str = Field(...)
    l_name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    role:str = Field(..., pattern="^(admin|teacher|student)$")

    @validator('password')
    def validate_password(cls, value):
        if len(value)<8:
            raise ValueError("Password must be atleast 8 character long.")
        if not any(char.isupper() for char in value): 
            raise ValueError("Password must contain atleast 1 Uppercase letter.")
        if not any(char.islower() for char in value): 
            raise ValueError("Password must contain atleast 1 Lowercase letter.")
        if not any(char in "!@#$%^&*()_+-=[]{}|;:'\",.<>?/" for char in value):
            raise ValueError("Password must contain atleast 1 special character.")
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "f_name" : "Parth",
                "l_name" : "Bapodara",
                "email" : "demo@gmail.com",
                "password" : "Weak@password",
                "role": "Admin or Teacher or Student"
            }
        }

class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    @validator('password')
    def validate_password(cls, value):
        if len(value)<8:
            raise ValueError("Password must be atleast 8 character long.")
        if not any(char.isupper() for char in value): 
            raise ValueError("Password must contain atleast 1 Uppercase letter.")
        if not any(char.islower() for char in value): 
            raise ValueError("Password must contain atleast 1 Lowercase letter.")
        if not any(char in "!@#$%^&*()_+-=[]{}|;:'\",.<>?/" for char in value):
            raise ValueError("Password must contain atleast 1 special character.")
        return value
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "demo@gmail.com",
                "password": "Weak@password"
            }
        }