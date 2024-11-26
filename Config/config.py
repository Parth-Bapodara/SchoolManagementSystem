from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "School Management System"
    version: str = "1.0"

    GOOGLE_CLIENT_ID: str  
    GOOGLE_CLIENT_SECRET: str 

    MAIL_PASSWORD: str
    MAIL_FROM: str

    DATABASE_URL_SQLITE: str = "sqlite:///./demo.db"
    DATABASE_URL_POSTGRESQL: str = "postgresql://postgres:Test@123@localhost/test_db"

    class Config():
        env_file = ".env"
    
settings=Settings()

    




# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
# from pydantic import BaseModel, EmailStr
# import random,os,smtplib
# from dotenv import load_dotenv
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from typing import Any

# load_dotenv()

# class EmailSettings(BaseModel):
#     MAIL_USERNAME: str = "parth.bapodara@mindinventory.com"
#     MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
#     MAIL_FROM: EmailStr = os.getenv("MAIL_FROM")
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
#     USE_CREDENTIALS=email_settings.USE_CREDENTIALS,
#     VALIDATE_CERTS=email_settings.VALIDATE_CERTS
# )

# def generate_verification_code() -> str:
#     return f"{random.randint(100000, 999999)}"

# def validate_email(email: str) -> bool:
#     try:
#         domain = email.split("@")[1]
#         smtp = smtplib.SMTP(f"smtp.{domain}", timeout=5)
#         smtp.quit()
#         return True
#     except:
#         return False

# async def send_verification_email(recipient_email: str, reset_code: str) -> None:
#     """Send a password reset email with a verification code."""
#     try:
#         msg = MIMEMultipart()
#         msg['From'] = email_settings.MAIL_FROM
#         msg['To'] = recipient_email
#         msg['Subject'] = "Password Reset Verification Code"

#         body = f"Your verification code is: {reset_code}. This code will expire in 15 minutes."
#         msg.attach(MIMEText(body, 'plain'))

#         # Sending the email
#         with smtplib.SMTP(email_settings.MAIL_SERVER, email_settings.MAIL_PORT) as server:
#             server.starttls()
#             server.login(email_settings.MAIL_USERNAME, email_settings.MAIL_PASSWORD)
#             text = msg.as_string()
#             server.sendmail(email_settings.MAIL_FROM, recipient_email, text)

#     except Exception as e:
#         print(f"Error sending email: {str(e)}")
#         raise Exception("Failed to send verification email.")

# GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
# GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


