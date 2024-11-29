from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.api.v1.user.schemas.forgot_password import PasswordResetRequest, PasswordResetVerify, ChangePassword
from src.api.v1.user.utils.forgot_password import UserService
from src.api.v1.security.security import JWTBearer
from Database.database import get_db
from src.api.v1.user.models.user_models import User

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
