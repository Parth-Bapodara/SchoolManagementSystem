from pydantic import BaseModel
from typing import Literal,Optional
from datetime import datetime,timedelta,timezone

#to record clock-in time of user
class AttendanceIn(BaseModel):
    clock_in: datetime

#to record clock-out time of user
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