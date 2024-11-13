# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
# from pydantic import BaseModel, EmailStr
# import random
# from typing import Optional

# # Email Configuration
# class EmailSettings(BaseModel):
#     MAIL_USERNAME: str = "parth.bapodara@mindinventory.com"
#     MAIL_PASSWORD: str = "P@RTh@@234"
#     MAIL_FROM: EmailStr = "parth.bapodara@mindinventory.com"
#     MAIL_SERVER: str = "smtp.gmail.com"
#     MAIL_PORT: int = 587
#     MAIL_STARTTLS: bool = True
#     MAIL_SSL_TLS: bool = False
#     USE_CREDENTIALS: bool = True
#     VALIDATE_CERTS: bool = True

# email_settings = EmailSettings()

# conf = ConnectionConfig(
#     MAIL_USERNAME=email_settings.MAIL_USERNAME,
#     MAIL_PASSWORD=email_settings.MAIL_PASSWORD,
#     MAIL_FROM=email_settings.MAIL_FROM,
#     MAIL_SERVER=email_settings.MAIL_SERVER,
#     MAIL_PORT=email_settings.MAIL_PORT,
#     MAIL_STARTTLS=email_settings.MAIL_STARTTLS,
#     MAIL_SSL_TLS=email_settings.MAIL_SSL_TLS,
#     USE_CREDENTIALS= email_settings.USE_CREDENTIALS,
#     VALIDATE_CERTS= email_settings.VALIDATE_CERTS
# )

# def generate_verification_code() -> str:
#     return f"{random.randint(100000, 999999)}"

# async def send_verification_email(email: EmailStr, code: str):
#     message = MessageSchema(
#         subject="Password Reset Code",
#         recipients=[email],
#         body=f"Your password reset code is: {code}",
#         subtype="plain"
#     )
#     fm = FastMail(conf)
#     await fm.send_message(message)


from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
import random,os
from dotenv import load_dotenv

load_dotenv()

class EmailSettings(BaseModel):
    MAIL_USERNAME: str = "apikey"
    MAIL_PASSWORD: str = os.getenv("SENDGRID_API_KEY")
    MAIL_FROM: EmailStr = os.getenv("MAIL_FROM")
    MAIL_SERVER: str = "smtp.sendgrid.net"
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

email_settings = EmailSettings()

def generate_verification_code() -> str:
    return f"{random.randint(100000, 999999)}"

conf = ConnectionConfig(
    MAIL_USERNAME=email_settings.MAIL_USERNAME,
    MAIL_PASSWORD=email_settings.MAIL_PASSWORD,
    MAIL_FROM=email_settings.MAIL_FROM,
    MAIL_SERVER=email_settings.MAIL_SERVER,
    MAIL_PORT=email_settings.MAIL_PORT,
    MAIL_STARTTLS=email_settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=email_settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=email_settings.USE_CREDENTIALS,
    VALIDATE_CERTS=email_settings.VALIDATE_CERTS
)

# Use FastMail to send emails via SendGrid's SMTP server
async def send_verification_email(email: EmailStr, code: str):
    message = MessageSchema(
        subject="Password Reset Code",
        recipients=[email],
        body=f"Your password reset code is: {code}",
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
