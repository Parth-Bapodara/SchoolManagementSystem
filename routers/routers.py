from fastapi import APIRouter
from src.api.v1.user.services.CRUD.user_create import router as user_create_router
from src.api.v1.user.services.CRUD.user_update import router as user_update_router
from src.api.v1.user.services.CRUD.view_user_info import router as view_info_router
from src.api.v1.user.services.CRUD.user_retrieval import router as user_retrieval
from src.api.v1.exam.services.class_management import router as class_management
from src.api.v1.user.services.Login.normal_login import router as login_router
from src.api.v1.user.services.Login.google_login import router as google_router
from src.api.v1.user.utils.forgot_password import router as forgot_password
from src.api.v1.attendance.services.attendance_services import router as attendance_services
from src.api.v1.exam.services.exam_services import router as exam_services

router = APIRouter()

router.include_router(user_create_router, tags=["User CRUD"])
router.include_router(user_update_router, tags=["User CRUD"])
router.include_router(view_info_router, tags=["User CRUD"])
router.include_router(user_retrieval, tags=["User Retrieval"])
router.include_router(login_router, tags=["Login"])
router.include_router(google_router, tags=["Login"])
router.include_router(forgot_password, tags=["Forgot Password"])
router.include_router(attendance_services, tags=["Attendance Management"])
router.include_router(class_management, tags=["Class Management"])
router.include_router(exam_services,tags=["Exam Management"])

