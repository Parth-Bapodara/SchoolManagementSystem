from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from database.base import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

#DB model representing a user with diffrent fields.
# class User(Base):
#     __tablename__ = "users"
    
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True, nullable=False)
#     hashed_password = Column(String, nullable=False)
#     passcode = Column(String,nullable=True)
#     role = Column(String, default="student", nullable=False)
#     username = Column(String, unique=True, nullable=False)
#     status = Column(String, default="active", nullable=False)

#     attendances = relationship("Attendance", back_populates="user")
#     exam_submissions = relationship("ExamSubmission", back_populates="student")
#     reset_requests = relationship("PasswordResetRequest", back_populates="user")

# #DB model representing a class with fields like id and name.
# class Class(Base):
#     __tablename__ = "classes"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True, nullable=False)

#     exams = relationship("Exam", back_populates="class_")

# #DB model representing a subject with fields like id and name.
# class Subject(Base):
#     __tablename__ = "subjects"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True, nullable=False)

#     exams = relationship("Exam", back_populates="subject")

# #DB model representing an exam with diffrent fields.
# class Exam(Base):
#     __tablename__ = "exams"

#     id = Column(Integer, primary_key=True, index=True)
#     subject_id = Column(Integer, ForeignKey("subjects.id"))
#     class_id = Column(Integer, ForeignKey("classes.id"))
#     date = Column(DateTime, nullable=False)
#     duration = Column(Integer, nullable=False)
#     created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
#     status = Column(String, default="scheduled")

#     submissions = relationship("ExamSubmission", back_populates="exam")
#     subject = relationship("Subject", back_populates="exams")
#     class_ = relationship("Class", back_populates="exams")
    
# DB model for attendence of user
# class Attendance(Base):
#     __tablename__ = "attendances"

#     id=Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     clock_in = Column(DateTime, default=datetime.utcnow)
#     clock_out = Column(DateTime, nullable=True)
#     hours_worked = Column(Float, default=0)

#     user = relationship("User", back_populates="attendances")

#     def calculate_hours_worked(self):
#         if self.clock_out:
#             return(self.clock_out-self.clock_in).total_seconds()/3600
#         return 0
    
# #DB model to track and manage student marks
# class ExamSubmission(Base):
#     __tablename__ = "exam_submissions"

#     id = Column(Integer, primary_key=True, index=True)
#     exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
#     student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     answers = Column(String, nullable=True)
#     marks = Column(Float, default=0)

#     exam = relationship("Exam", back_populates="submissions")
#     student = relationship("User", back_populates="exam_submissions")

# #DB model to execute password reset functionality
# class PasswordResetRequest(Base):
#     __tablename__ = "password_reset_requests"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     reset_code = Column(String, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     expiry_time = Column(DateTime, nullable=False)

#     user = relationship("User", back_populates="reset_requests")

#     def __init__(self, user_id, reset_code, expiry_time):
#         self.user_id = user_id
#         self.reset_code = reset_code
#         self.expiry_time = expiry_time
