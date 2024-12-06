from fastapi import FastAPI
from src.api.v1.utils.response_utils import Response
from src.api.v1.user.schemas.forgot_password import Phone,VerifyOTP
from src.api.v1.user.utils.email_utils import generate_verification_code,send_otp

otp_storage={}

class MobileOTPGenration:

    def send_otp_route(phone: Phone):
        otp = generate_verification_code()
        otp_storage[phone.phone_number] = otp
        send_otp(phone.phone_number, otp)
        return Response(status_code=200, message="OTP send to Given Mobile Number", data={}).send_success_response()
    
    def verify_otp_route(otp_data: VerifyOTP):
        stored_otp = otp_storage.get(otp_data.phone_number)

        if not stored_otp:
            return Response(status_code=400, message="OTP not found.Kindly check Phone number and Enterted OTP are correct.", data={}).send_error_response()
        
        if stored_otp != otp_data.otp:
            return Response(status_code=400, message="Inavlid OTP. Kindly check and input again", data={}).send_error_response()
        
        # del otp_storage(otp_data.phone_number)

        return Response(status_code=200, message="OTP verfified successfully.", data={}).send_success_response()

