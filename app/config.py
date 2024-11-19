from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
import random,os,smtplib
from dotenv import load_dotenv

load_dotenv()

class EmailSettings(BaseModel):
    MAIL_USERNAME: str = "parth.bapodara@mindinventory.com"
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: EmailStr = os.getenv("MAIL_FROM")
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

email_settings = EmailSettings()

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

def generate_verification_code() -> str:
    return f"{random.randint(100000, 999999)}"

def validate_email(email: str) -> bool:
    try:
        domain = email.split("@")[1]
        smtp = smtplib.SMTP(f"smtp.{domain}", timeout=5)
        smtp.quit()
        return True
    except:
        return False

GOOGLE_CLIENT_ID = "514425638136-3mvsn0f064gc08qs2o2kufkgcc0il6ov.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_REDIRECT_URI = "http://127.0.0.1:8000/google/callback/"

# class EmailSettings(BaseModel):
#     MAIL_USERNAME: str = "apikey"
#     MAIL_PASSWORD: str = os.getenv("SENDGRID_API_KEY")
#     MAIL_FROM: EmailStr = os.getenv("MAIL_FROM")
#     MAIL_SERVER: str = "smtp.sendgrid.net"
#     MAIL_PORT: int = 587
#     MAIL_STARTTLS: bool = True
#     MAIL_SSL_TLS: bool = False
#     USE_CREDENTIALS: bool = True
#     VALIDATE_CERTS: bool = True