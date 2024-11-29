from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.api.v1.attendance.models.attendance_models import Attendance
from src.api.v1.utils.response_utils import Response
from fastapi import HTTPException
from src.api.v1.security.security import get_current_user  # Function to get current user from JWT
from src.api.v1.user.models.user_models import User

class AttendanceServices:

    @staticmethod
    def clock_in_user(db: Session, current_user: User):
        """
        Clock-in a user for the day.
        """
        today_date = datetime.utcnow().date()

        # Check if the user has already clocked in today (maximum of 5 clock-ins)
        today_clockins = db.query(Attendance).filter(
            Attendance.user_id == current_user.id,
            Attendance.clock_in >= datetime(today_date.year, today_date.month, today_date.day)
        ).count()

        if today_clockins >= 5:
            return Response(
                status_code=400,
                message="Maximum number of clock-ins reached for today.",
                data={}
            ).send_error_response()

        # Clock-in the user
        attendance = Attendance(user_id=current_user.id, clock_in=datetime.utcnow())
        db.add(attendance)
        db.commit()
        db.refresh(attendance)

        return Response(
            status_code=201,
            message="Clock-in successful.",
            data=attendance
        ).send_success_response()

    @staticmethod
    def clock_out_user(db: Session, current_user: User):
        """
        Clock-out a user.
        """
        # Find the most recent clock-in that does not yet have a clock-out
        attendance = db.query(Attendance).filter(
            Attendance.user_id == current_user.id,
            Attendance.clock_out == None
        ).order_by(Attendance.clock_in.desc()).first()

        if not attendance:
            return Response(
                status_code=404,
                message="No open clock-in found for this user.",
                data={}
            ).send_error_response()

        # Clock-out the user
        attendance.clock_out = datetime.utcnow()
        attendance.hours_worked = attendance.calculate_hours_worked()  # Assuming this method exists to calculate hours
        db.commit()
        db.refresh(attendance)

        return Response(
            status_code=200,
            message="Clock-out successful.",
            data=attendance
        ).send_success_response()

    @staticmethod
    def get_weekly_report(db: Session, current_user: User):
        """
        Get total hours worked and distinct days worked in the last week.
        """
        one_week_ago = datetime.utcnow() - timedelta(days=7)

        # Query attendances in the last week for the current user
        attendances = db.query(Attendance).filter(
            Attendance.user_id == current_user.id,
            Attendance.clock_in >= one_week_ago
        ).all()

        # Calculate total hours worked and distinct days worked
        total_hours = sum(attendance.hours_worked for attendance in attendances if attendance.clock_out)
        worked_days = {attendance.clock_in.date() for attendance in attendances if attendance.clock_out}
        distinct_days_count = len(worked_days)

        return Response(
            status_code=200,
            message="Weekly report retrieved successfully.",
            data={"total_hours_worked": round(total_hours, 2), "distinct_days_worked": distinct_days_count}
        ).send_success_response()
