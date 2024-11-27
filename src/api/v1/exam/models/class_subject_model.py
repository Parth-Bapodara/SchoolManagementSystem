from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from Database.database import Base
from sqlalchemy.orm import relationship

#DB model representing a class with fields like id and name.
class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    exams = relationship("Exam", back_populates="class_")

    class Config:
        orm_mode = True

#DB model representing a subject with fields like id and name.
class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    exams = relationship("Exam", back_populates="subject")

    class Config:
        orm_mode = True