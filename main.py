from fastapi import FastAPI
from routers.routers import router
from starlette.middleware.sessions import SessionMiddleware
from Config.config import settings
from src.api.v1.seed_admin import seed_data
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="School Management System", version="1.0",)
app.add_middleware(SessionMiddleware, secret_key=settings.GOOGLE_CLIENT_SECRET)

app.include_router(router)

app.mount("/exam_papers", StaticFiles(directory="/home/python/Desktop/Parth/School-Management-System/uploads/exam_papers"), name="exam_papers")

@app.on_event("startup")
async def startup_event():
    seed_data()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)