from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from Database.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
#from src.api.v1.user.models.user_models import User

#DB model representing a class with fields like id and name.
class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    exams = relationship("Exam", back_populates="class_")

#DB model representing a subject with fields like id and name.
class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    exams = relationship("Exam", back_populates="subject")

#DB model representing an exam with diffrent fields.
class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    class_id = Column(Integer, ForeignKey("classes.id"))
    date = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="scheduled")

    submissions = relationship("ExamSubmission", back_populates="exam")
    subject = relationship("Subject", back_populates="exams")
    class_ = relationship("Class", back_populates="exams")

#DB model to track and manage student marks
class ExamSubmission(Base):
    __tablename__ = "exam_submissions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    answers = Column(String, nullable=True)
    marks = Column(Float, default=0)

    exam = relationship("Exam", back_populates="submissions")
    student = relationship("User", back_populates="exam_submissions")