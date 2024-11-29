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
            # Decode the token and extract user data
            user_data = security.decode_access_token(token)
        except JWTError:
            return Response(status_code=403, message="Invalid token", data={}).send_error_response

        # Check if the user is an admin
        if user_data.get("role") != "admin":
            return Response(
                status_code=403,
                message=f"Not authorized to view {role}s. Only admins can access this data.",
                data={}
            ).send_error_response()

        # Calculate pagination
        skip, limit = UserService.get_skip_and_limit(page, limit)

        # Query the database for users based on role
        users = db.query(User).filter(User.role == role).offset(skip).limit(limit).all()
        if not users:
            return {"msg": f"No {role}s found."}

        return {
            "page": page,
            "limit": limit,
            f"{role}s": [{"Email": user.email, "Role": user.role, "ID": user.id, "User_name": user.username, "Status": user.status} for user in users]
        }

# Helper function to extract user from the token
async def get_current_user(token: str = Depends(JWTBearer())):
    """
    This helper function decodes the JWT token, extracts user data,
    and returns the current user.
    """
    try:
        user_data = security.decode_jwt(token)  # Decode token and extract user data
    except JWTError:
        return Response(status_code=403, message="Invalid token", data={}).send_error_response()

    return user_data  # You can now use this user data throughout your routes
