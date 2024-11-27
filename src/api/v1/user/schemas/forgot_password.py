from pydantic import BaseModel, Field, validator, EmailStr, model_validator
from typing import Literal,Optional
import re
from datetime import datetime,timedelta,timezone

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
    
    @validator("confirm_password")
    def check_password_match(cls, confirm_password, values):
        if "new_password" in values and confirm_password != values["new_password"]:
            raise ValueError("The passwords do not match.")
        return confirm_password

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

    @validator("confirm_password")
    def check_password_match(cls, confirm_password, values):
        if "new_password" in values and confirm_password != values["new_password"]:
            raise ValueError("The passwords do not match.")
        return confirm_password
    
#to pass simple message
class Message(BaseModel):
    message:str