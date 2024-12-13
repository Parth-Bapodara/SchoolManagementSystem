from pydantic import BaseModel

class Class_Subject(BaseModel):
    class_name: str
    subject_name: str
    student_name: str
    marks: int
    
    