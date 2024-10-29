from sqlalchemy import Column, String
from app.database import Base

class Admin(Base):
    __tablename__ = "admins"
    email = Column(String, primary_key = True, index = True)
    f_name = Column(String)
    l_name = Column(String)
    password  = Column(String)

class User(Base):
    __tablename__ = "users"
    email = Column(String, primary_key = True, index = True)
    f_name = Column(String)
    l_name = Column(String)
    role = Column(String)
    password = Column(String)