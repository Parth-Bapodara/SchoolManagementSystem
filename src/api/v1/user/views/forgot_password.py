from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.v1.user.schemas.forgot_password import PasswordResetRequest, PasswordResetVerify, ChangePassword, Phone, PasswordResetVerifyMob
from src.api.v1.utils.response_utils import Response
from src.api.v1.user.services.Login.user_auth import UserService
from src.api.v1.security.security import JWTBearer
from Database.database import get_db
from src.api.v1.user.models.user_models import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/password-reset-request/")
async def password_reset_request(data: PasswordResetRequest, db: Session = Depends(get_db)):
    return await UserService.password_reset_request(db, data.email)

@router.post("/password-reset/")
async def password_reset(data: PasswordResetVerify, db: Session = Depends(get_db)):
    """Reset password using a verification code."""
    return await UserService.password_reset(data, db)

@router.post("/password-change/")
async def change_password(data: ChangePassword, current_user: User = Depends(JWTBearer()), db: Session = Depends(get_db)):
    """Change the current user's password."""
    return UserService.change_password(db, current_user, data.old_password, data.new_password, data.confirm_password)

@router.post("/reset-password-mobile")
async def password_reset_by_mobile(data: Phone, db:Session = Depends(get_db)):
    cleaned_phone_number = ''.join(filter(str.isdigit, data.phone_number))

    if not cleaned_phone_number.isdigit():
        return Response(status_code=400, message="Invalid phone number format", data={}).send_error_response()
    
    mobile_no = int(cleaned_phone_number)
    
    return UserService.password_reset_by_mobile(db, mobile_no)

@router.post("/reset-response-mobile")
async def password_response_by_mobile(data: PasswordResetVerifyMob, db:Session = Depends(get_db)):
    return await UserService.password_reset_mob(data, db)