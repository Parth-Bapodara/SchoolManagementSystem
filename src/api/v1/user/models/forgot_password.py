from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from Database.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

class PasswordResetRequest(Base):
    __tablename__ = "password_reset_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reset_code = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expiry_time = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="reset_requests")

    def __init__(self, user_id, reset_code, expiry_time):
        self.user_id = user_id
        self.reset_code = reset_code
        self.expiry_time = expiry_time
                                                                                            