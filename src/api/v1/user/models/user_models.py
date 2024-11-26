from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship,class_mapper
from Database.database import Base
from src.api.v1.attendance.models.attendance_models import Attendance
from src.api.v1.user.models.forgot_password import PasswordResetRequest
from src.api.v1.exam.models.exam_models import ExamSubmission,Exam

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    passcode = Column(String, nullable=True)
    role = Column(String, default="student", nullable=False)
    username = Column(String, unique=True, nullable=False)
    status = Column(String, default="active", nullable=False)

    attendances = relationship("Attendance", back_populates="user")
    exam_submissions = relationship("ExamSubmission", back_populates="student")
    reset_requests = relationship("PasswordResetRequest", back_populates="user")

