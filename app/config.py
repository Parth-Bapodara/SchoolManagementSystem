import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class EmailSettings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 443
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_TLS_SSL: bool = True
    MAIL_STARTTLS: bool = False
    USE_CREDENTIALS: bool = True
    # TEMPLATE_FOLDER: str = "None"  
    MAIL_FROM_NAME: str

    class Config:
        env_file = ".env"

email_settings = EmailSettings()

try:
    with smtplib.SMTP(email_settings.MAIL_SERVER, email_settings.MAIL_PORT) as server:
        server.starttls() if email_settings.MAIL_STARTTLS else None
        server.login(email_settings.MAIL_USERNAME, email_settings.MAIL_PASSWORD)

        msg = MIMEMultipart()
        msg['From'] = email_settings.MAIL_FROM
        msg['To'] = "khushbu.chhikniwala@mindinventory.com"
        msg['Subject'] = "Test Email"
        body = "This is a test email sent from Python."
        msg.attach(MIMEText(body, 'plain'))

        server.sendmail(email_settings.MAIL_FROM, "khushbu.chhikniwala@mindinventory.com", msg.as_string())
        print("Email sent successfully!")

except Exception as e:
    print(f"Failed to send email: {e}")
