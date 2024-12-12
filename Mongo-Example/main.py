from fastapi import FastAPI
from Exam.routes.routes import router

app = FastAPI()

app.include_router(router)
