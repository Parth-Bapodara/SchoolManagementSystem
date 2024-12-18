from pydantic_settings import BaseSettings
from typing import Optional
import boto3, os

class Settings(BaseSettings):
    app_name: str = "School Management System"
    version: str = "1.0"

    GOOGLE_CLIENT_ID: str  
    GOOGLE_CLIENT_SECRET: str 

    MAIL_PASSWORD: str
    MAIL_FROM: str

    DATABASE_URL_SQLITE: str = "sqlite:///./demo.db"
    DATABASE_URL_POSTGRESQL: str = "postgresql://postgres:Test@123@localhost/test_db"

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET_NAME: str
    AWS_REGION: str

    FACEBOOK_CLIENT_ID: int
    FACEBOOK_CLIENT_SECRET: str
    FACEBOOK_API_VERSION: str

    # APPLE_CLIENT_ID: str
    # APPLE_TEAM_ID: str
    # APPLE_KEY: str
    # APPLE_SECRET_ID: str

    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: int

    OPENWEATHER_API_KEY: str
    
    class Config():
        env_file = ".env"
    
settings=Settings()

    
