from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
import random,os,smtplib
from Config.config import settings
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import logging

class EmailSettings(BaseModel):
    MAIL_USERNAME: str = "parth.bapodara@mindinventory.com"
    MAIL_PASSWORD: str = settings.MAIL_PASSWORD
    MAIL_FROM: EmailStr = settings.MAIL_FROM
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

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def send_otp(phone_number, otp):
    message= f"Your OTP is: {otp}"
    client.messages.create(to=phone_number, from_=settings.TWILIO_PHONE_NUMBER, body=message)

def validate_email(email: str) -> bool:
    try:
        domain = email.split("@")[1]
        smtp = smtplib.SMTP(f"smtp.{domain}", timeout=5)
        smtp.quit()
        return True
    except:
        return False

async def send_verification_email(recipient_email: str, reset_code: str) -> None:
    """Send a password reset email with a verification code."""
    try:
        msg = MIMEMultipart()
        msg['From'] = email_settings.MAIL_FROM
        msg['To'] = recipient_email
        msg['Subject'] = "Password Reset Verification Code"

        body = f"Your verification code is: {reset_code}. This code will expire in 15 minutes."
        msg.attach(MIMEText(body, 'plain'))

        # Sending the email
        with smtplib.SMTP(email_settings.MAIL_SERVER, email_settings.MAIL_PORT) as server:
            server.starttls()
            server.login(email_settings.MAIL_USERNAME, email_settings.MAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(email_settings.MAIL_FROM, recipient_email, text)

        logging.info(f"Verification email sent to {recipient_email}")

    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        raise Exception("Failed to send verification email.")

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET

