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

    
