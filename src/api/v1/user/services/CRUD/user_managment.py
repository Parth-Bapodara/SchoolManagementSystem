from jose import JWTError
from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.api.v1.user.models.user_models import User
from src.api.v1.security.security import SECRET_KEY, ALGORITHM, get_password_hash, decode_access_token 
from src.api.v1.utils.response_utils import Response
from src.api.v1.user.schemas.user_schemas import UserCreate, UserUpdate, UserInDb
from src.api.v1.security import security
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

logger.setLevel(logging.DEBUG)

DEFAULT_PAGE = 1
DEFAULT_LIMIT = 5

class UserServices:

    @staticmethod
    def create_user(db: Session, user_data: UserCreate, token: str):
        try:
            logger.info(f"Received token: {token}")
            
            user_data_decoded = decode_access_token(token)
            logging.info(f"Decoded token: {user_data_decoded}")
        except Exception as e:
            logging.error(f"Error decoding token: {str(e)}")
            return Response(status_code=403, message="Token is invalid or expired.", data={}).send_error_response()

        if user_data_decoded.get("role") != "admin":
            logging.warning("Unauthorized access attempt")
            return Response(
                status_code=403,
                message="Only admins can create new users.",
                data={}
            ).send_error_response()

        existing_user = db.query(User).filter(or_(User.email == user_data.email, User.username == user_data.username)).first()

        if existing_user:
            if existing_user.email == user_data.email:
                return Response(status_code=400, message="Email already in use.", data={}).send_error_response()
            elif existing_user.username == user_data.username:
                return Response(status_code=400, message="Username already in use.", data={}).send_error_response()
            elif existing_user.mobile_no == user_data.mobile_no:
                return Response(status_code=400, message="Mobile Number already Exists.", data={}).send_error_response()

        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role,
            username=user_data.username,
            status="active",
            mobile_no = user_data.mobile_no
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {"msg": f"{user_data.role.capitalize()} created successfully", "email": db_user.email, "id": db_user.id, "role": db_user.role, "mobile_no": db_user.mobile_no}

    @staticmethod
    def update_user(db:Session, user_data: UserUpdate, token:str):
        pass
    
    @staticmethod
    def get_user_info(db: Session, token: str):
        try:
            user_data = decode_access_token(token)
            user_id = user_data["sub"]  
        except Exception as e:
            return Response(status_code=403, message="Invalid or expired token", data={}).send_error_response()

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return user
        return Response(status_code=404, message="User not found", data={}).send_error_response()

    @staticmethod
    def delete_user(db: Session, user_id: int, user_data: dict):
        try:
            if user_data.get("role") != "admin":
                return Response(status_code=403, message="Admin privileges required", data={}).send_error_response()
        except Exception as e:
            return Response(status_code=403, message="Invalid or expired token", data={e}).send_error_response()

        user_to_delete = db.query(User).filter(User.id == user_id).first()
        if user_to_delete:
            db.delete(user_to_delete)
            db.commit()
            return Response(status_code=200, message="User deleted successfully.", data={user_to_delete})
        
        return Response(status_code=404, message="User not found", data={}).send_error_response()

    @staticmethod
    def get_users_by_role(db: Session, token: str, role: str, page: int, limit: int):
        """Fetch users by role (admin, student, or teacher)."""
        try:
            user_data = security.decode_access_token(token)
        except JWTError:
            return Response(status_code=403, message="Invalid token", data={}).send_error_response

        if user_data.get("role") != "admin":
            return Response(
                status_code=403,
                message=f"Not authorized to view {role}s. Only admins can access this data.",
                data={}
            ).send_error_response()

        limit = min(limit, 5)

        total_users= db.query(User).count()
        skip = (page - 1)* limit

        users = db.query(User).filter(User.role == role).offset(skip).limit(limit).all()
        if not users:
            if skip >= total_users:
                return Response(
                    status_code = 400,
                    message="Page exceeds the number of available users.", 
                    data={}
                ).send_error_response()
            return Response(
                status_code=404, 
                message=f"No {role}s found.", 
                data={}
            ).send_error_response()
        
        total_pages=(total_users + limit - 1) // limit

        return Response(
            status_code=200,
            message="Information Retrieved Successfully.",
            data={
            "page": page,
            "limit": limit,
            "total_users": total_users, 
            "total_pages": total_pages, 
            f"{role}s": [{"Email": user.email, "Role": user.role, "ID": user.id, "User_name": user.username, "Status": user.status, "Mobile No": user.mobile_no} for user in users]}
        ).send_success_response()
