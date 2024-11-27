from pydantic import BaseModel, Field, validator, EmailStr, model_validator

class ClassCreate(BaseModel):
    name:str
    
    @validator('name')
    def password_complexity(cls,value):
        if len(value) < 2:
            raise ValueError("Class name atleast contain 2 or more Characters.")
        return value

#For creating new diffrent Subjects
class SubjectCreate(BaseModel):
    name:str

    @validator('name')
    def password_complexity(cls,value):
        if len(value) < 3:
            raise ValueError("Subject name atleast contain 3 or more Characters and no Abbreviations.")
        return value