from fastapi import FastAPI
from app.api import admin,user
from app.database import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(admin.router)
app.include_router(user.router)
