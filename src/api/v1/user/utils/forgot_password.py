from fastapi import FastAPI, Depends, HTTPException, status, Request, APIRouter
from sqlalchemy.orm import Session
from src.api.v1.security import security
from src.api.v1.user.models.user_models import User
from Database.database import get_db, Base, engine
from datetime import timedelta, datetime, timezone
from Config.config import settings
from src.api.v1.user.schemas import forgot_password
from src.api.v1.user.utils.email_utils import generate_verification_code,send_verification_email
from src.api.v1.user.models.forgot_password import PasswordResetRequest
from src.api.v1.user.schemas.forgot_password import ChangePassword,PasswordResetVerify,Message

router = APIRouter()
Base.metadata.create_all(bind=engine)

@router.post("/password-reset-request/")
async def password_reset_request(data: forgot_password.PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_code = generate_verification_code()
    expiry_time = datetime.utcnow() + timedelta(minutes=15)

    reset_request = PasswordResetRequest(user_id=user.id, reset_code=reset_code, expiry_time=expiry_time)
    db.add(reset_request)
    db.commit()

    await send_verification_email(data.email, reset_code)
    return {"message": "Verification code sent to your email"}

@router.post("/password-reset/")
async def password_reset(data: PasswordResetVerify, db: Session = Depends(get_db)):
    reset_request = db.query(PasswordResetRequest).join(User).filter(
        User.email == data.email, PasswordResetRequest.reset_code == data.code
    ).first()

    if not reset_request:
        raise HTTPException(status_code=400, detail="Invalid code or email")

    if reset_request.expiry_time < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset code has expired")

    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="new Password and Confirm Password do not match")

    if len(data.new_password) < 8 or not any(char.isdigit() for char in data.new_password) or not any(char.isupper() for char in data.new_password):
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long, contain one digit, and one uppercase letter")

    user.hashed_password = security.get_password_hash(data.new_password)
    db.commit()
    db.delete(reset_request)
    db.commit()

    return {"message": "Password reset successfully."}

@router.post("/password-change/")
async def change_password(data: ChangePassword, current_user: User = Depends(security.get_current_user), db: Session = Depends(get_db)):

    if not security.pwd_context.verify(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="New password and Confirm password do not match")
    if len(data.new_password) < 8 or not any(char.isdigit() for char in data.new_password) or not any(char.isupper() for char in data.new_password):
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long, contain one digit, and one uppercase letter")

    current_user.hashed_password = security.pwd_context.hash(data.new_password)
    db.commit()

    return {"message": "Password changed successfully"}