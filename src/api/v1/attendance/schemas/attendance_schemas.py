from pydantic import BaseModel, Field, validator, EmailStr, model_validator
from typing import Literal,Optional
import re
from datetime import datetime,timedelta,timezone

class AttendanceIn(BaseModel):
    clock_in: datetime

#to clock out user
class AttendanceOut(BaseModel):
    clock_out: datetime

#to check attendance details
class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    clock_in: datetime
    clock_out: Optional[datetime]
    hours_worked: float

    class Config:
        orm_mode = True

#to get weekly report of users
class WeeklyReportResponse(BaseModel):
    total_hours_worked: float
    distinct_days_worked: int