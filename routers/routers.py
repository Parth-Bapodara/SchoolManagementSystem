from fastapi import APIRouter
from src.api.v1.user.views.user_managment import router as user_management_router
from src.api.v1.user.views.user_retrieval import router as user_retrieval_router

from src.api.v1.exam.views.class_subject_view import router as Class_and_Subject
from src.api.v1.exam.views.exam_view import router as Exam_Management
from src.api.v1.exam.views.marks_view import router as Marks_management

from src.api.v1.user.services.Login.normal_login import router as login_router
from src.api.v1.user.services.Login.google_login import router as google_router
from src.api.v1.user.utils.forgot_password import router as forgot_password
from src.api.v1.attendance.view.views import router as attendance_services

router = APIRouter()

router.include_router(user_management_router,tags=["User Management"])
router.include_router(user_retrieval_router, tags=["User Retrieval"])

router.include_router(Class_and_Subject, tags=["Class&Subject Management"])
router.include_router(Exam_Management, tags=["Exam Management"])
router.include_router(Marks_management, tags=["Marks Management"])

router.include_router(login_router, tags=["Login"])
router.include_router(google_router, tags=["Login"])
router.include_router(forgot_password, tags=["Forgot Password"])
router.include_router(attendance_services, tags=["Attendance Management"])

