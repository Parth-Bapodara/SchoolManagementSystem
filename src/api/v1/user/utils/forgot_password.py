from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from src.api.v1.user.utils.email_utils import send_verification_email, generate_verification_code
from src.api.v1.user.models.user_models import User
from src.api.v1.user.models.forgot_password import PasswordResetRequest
from src.api.v1.user.schemas.forgot_password import ChangePassword,PasswordResetVerify,Message
from src.api.v1.security import security
import logging
from src.api.v1.utils.response_utils import Response

class UserService:
    @staticmethod
    async def password_reset_request(db: Session, email: str):
        """Request a password reset and send the verification code via email."""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logging.error(f"User with email {email} not found.")
            return Response(status_code=404, message="User not found in our system. Check your email and please try again.", data={}).send_error_response()

        # Generate reset code and expiry time
        reset_code = generate_verification_code()
        expiry_time = datetime.utcnow() + timedelta(minutes=15)

        # Create a reset request in the database
        reset_request = PasswordResetRequest(user_id=user.id, reset_code=reset_code, expiry_time=expiry_time)
        db.add(reset_request)
        db.commit()

        # Send reset email with verification code
        try:
            await send_verification_email(email, reset_code)
        except Exception as e:
            logging.error(f"Error sending verification email to {email}: {e}")
            return Response(status_code=500, message="Failed to send verification email. Please try again later.", data={}).send_error_response()

        logging.info(f"Verification code sent to {email}")
        return Response(status_code=200, message="Verification code sent to your email", data={}).send_success_response()

    @staticmethod
    async def password_reset(data: PasswordResetVerify, db: Session):
        """Reset the user's password."""
        reset_request = db.query(PasswordResetRequest).join(User).filter(
            User.email == data.email, PasswordResetRequest.reset_code == data.code
        ).first()

        if not reset_request:
            return Response(status_code=400, message="Invalid code or email", data={}).send_error_response()

        if reset_request.expiry_time < datetime.utcnow():
            return Response(status_code=400, message="Reset code has expired", data={}).send_error_response()

        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            return Response(status_code=404, message="User not found", data={}).send_error_response()

        # At this point, password validation is already done by Pydantic validators
        user.hashed_password = security.get_password_hash(data.new_password)
        db.commit()

        db.delete(reset_request)  # Delete the reset request after successful password reset
        db.commit()

        logging.info(f"Password reset successfully for user {user.email}")
        return Response(status_code=200, message="Password reset successfully.", data={}).send_success_response()

    @staticmethod
    async def change_password(data: ChangePassword, current_user: User, db: Session):
        """Change the user's current password."""
        if not security.pwd_context.verify(data.old_password, current_user.hashed_password):
            return Response(status_code=400, message="Incorrect old password", data={}).send_error_response()

        if data.new_password != data.confirm_password:
            return Response(status_code=400, message="New password and confirm password do not match", data={}).send_error_response()

        if len(data.new_password) < 8 or not any(char.isdigit() for char in data.new_password) or not any(char.isupper() for char in data.new_password):
            return Response(status_code=400, message="Password must be at least 8 characters long, contain one digit, and one uppercase letter", data={}).send_error_response()

        current_user.hashed_password = security.pwd_context.hash(data.new_password)
        db.commit()

        logging.info(f"Password changed successfully for user {current_user.email}")
        return Response(status_code=200, message="Password changed successfully", data={}).send_success_response()
