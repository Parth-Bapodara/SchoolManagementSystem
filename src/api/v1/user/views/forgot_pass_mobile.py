from fastapi import APIRouter
from src.api.v1.user.services.Login.forgot_pass_mobile import MobileOTPGenration
from src.api.v1.user.schemas.forgot_password import Phone,VerifyOTP

router = APIRouter()

@router.post("/send-otp")
async def send_otp_route(phone: Phone):
    return MobileOTPGenration.send_otp_route(phone)


