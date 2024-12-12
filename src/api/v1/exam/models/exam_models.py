from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from Database.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta,timezone

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
    exam_pdf = Column(String, nullable=True)

    submissions = relationship("ExamSubmission", back_populates="exam")
    subject = relationship("Subject", back_populates="exams")
    class_ = relationship("Class", back_populates="exams")

    def update_status(self):
        if self.date < datetime.now(timezone.utc):
            self.status = "finished"

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