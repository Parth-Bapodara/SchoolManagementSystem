from pydantic import BaseModel, Field, field_validator, EmailStr, model_validator
from typing import Literal,Optional
import re
from datetime import datetime,timedelta,timezone
from src.api.v1.utils.response_utils import Response

class PasswordResetRequest(BaseModel):
    email: EmailStr

#to verify the generated user request for password reset
class PasswordResetVerify(BaseModel):
    email: EmailStr = Field(example="user@example.com")
    code: str = Field(example="123456")
    new_password: str = Field(example="Demo@1234")
    confirm_password: str = Field(example="Demo@1234")

    # Optional: validate password complexity
    @field_validator("new_password")
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit.")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter.")
        return password
    
    @model_validator(mode="before")
    def check_password_match(cls, values):
        if "new_password" in values and "confirm_password" in values:
            if values["new_password"] != values["confirm_password"]:
                raise ValueError("The passwords do not match.")
        return values

class PasswordResetVerifyMob(BaseModel):
    code: str = Field(example="Test@1234")
    new_password: str = Field(example="Demo@1234")
    confirm_password: str = Field(example="Demo@1234")

    # Optional: validate password complexity
    @field_validator("new_password")
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit.")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter.")
        return password
    
    @model_validator(mode="before")
    def check_password_match(cls, values):
        if "new_password" in values and "confirm_password" in values:
            if values["new_password"] != values["confirm_password"]:
                raise ValueError("The passwords do not match.")
        return values

#to change user password
class ChangePassword(BaseModel):
    old_password: str = Field()
    new_password: str = Field(...,example="Demo@1234")
    confirm_password: str = Field(...,example="Demo@1234")

    @field_validator("new_password")
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit.")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter.")
        return password

    @model_validator(mode="before")
    def check_password_match(cls, values):
        if "new_password" in values and "confirm_password" in values:
            if values["new_password"] != values["confirm_password"]:
                raise ValueError("The passwords do not match.")
        return values
    
#to pass simple message
class Message(BaseModel):
    message:str

#to pass mobile/phone number to generate OTP for password reset
class Phone(BaseModel):
    phone_number: str = Field(example="911234567890")



# class VerifyOTP(BaseModel):
#     mobile_no: str
#     otp: str
    
#     @field_validator("mobile_no")
#     def validate_mobile(cls, mobile_no):
#         if len(mobile_no) < 12:
#             raise ValueError("Invalid or Missing Mobile Number.Please check and try again.")
        
        
    