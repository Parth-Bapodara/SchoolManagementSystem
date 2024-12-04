from sqlalchemy.orm import Session
from src.api.v1.user.models.user_models import User
from src.api.v1.security import security
from src.api.v1.utils.response_utils import Response
from fastapi import HTTPException,Depends
from src.api.v1.security.security import JWTBearer
from jose import JWTError

DEFAULT_PAGE = 1
DEFAULT_LIMIT = 5

class UserService:

    @staticmethod
    def get_skip_and_limit(page: int, limit: int):
        """Helper function to calculate skip and limit for pagination."""
        skip = (page - 1) * limit
        return skip, limit

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

        skip, limit = UserService.get_skip_and_limit(page, limit)
        total_users= db.query(User).count()

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
            f"{role}s": [{"Email": user.email, "Role": user.role, "ID": user.id, "User_name": user.username, "Status": user.status} for user in users]}
        ).send_success_response()

# Helper function to extract user from the token
async def get_current_user(token: str = Depends(JWTBearer())):
    """
    This helper function decodes the JWT token, extracts user data,
    and returns the current user.
    """
    try:
        user_data = security.decode_jwt(token) 
    except JWTError:
        return Response(status_code=403, message="Invalid token", data={}).send_error_response()

    return user_data  