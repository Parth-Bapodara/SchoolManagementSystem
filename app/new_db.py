from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Replace with your own PostgreSQL instance
DATABASE_URL = 'postgresql://postgres:Test_123@localhost/test_db'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)