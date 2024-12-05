from fastapi import APIRouter
from src.api.v1.user.views.user_managment import router as user_management_router
from src.api.v1.user.views.user_retrieval import router as user_retrieval_router

from src.api.v1.exam.views.class_subject_view import router as Class_and_Subject
from src.api.v1.exam.views.exam_view import router as Exam_Management
from src.api.v1.exam.views.marks_view import router as Marks_management

from src.api.v1.user.views.user_nomral_login import router as User_Login
from src.api.v1.user.views.forgot_password import router as Forgot_Password
from src.api.v1.attendance.view.views import router as attendance_services

from src.api.v1.user.views.forgot_pass_mobile import router as Forgot_Pass_Mobile

router = APIRouter()

router.include_router(user_management_router,tags=["User Management"])
router.include_router(user_retrieval_router, tags=["User Retrieval"])

router.include_router(Class_and_Subject, tags=["Class&Subject Management"])
router.include_router(Exam_Management, tags=["Exam Management"])
router.include_router(Marks_management, tags=["Marks Management"])

router.include_router(User_Login, tags=["User Login"])
router.include_router(Forgot_Password, tags=["Forgot Password"])
router.include_router(attendance_services, tags=["Attendance Management"])
router.include_router(Forgot_Pass_Mobile, tags=["Test Router"])

