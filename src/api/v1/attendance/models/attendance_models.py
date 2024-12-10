from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from Database.database import Base

class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    clock_in = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None))
    clock_out = Column(DateTime, nullable=True)
    hours_worked = Column(Float, default=0)

    user = relationship("User", back_populates="attendances") 
    
    def calculate_hours_worked(self):
        if self.clock_out:
            return (self.clock_out - self.clock_in).total_seconds() / 3600
        return 0
