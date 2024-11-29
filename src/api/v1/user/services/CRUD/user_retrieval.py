from sqlalchemy.orm import Session
from src.api.v1.user.models.user_models import User
from src.api.v1.security import security
from src.api.v1.utils.response_utils import Response
from fastapi import Depends, HTTPException
from src.api.v1.security.security import JWTBearer
from jose import jwt,JWTError

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
            user_data = security.decode_jwt(token)
        except JWTError:
            raise HTTPException(status_code=403, detail="Invalid token")

        # Check if the user is an admin
        if user_data.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail=f"Not authorized to view {role}s. Only admins can access this data."
            )

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
    user_data = security.decode_jwt(token)  # Decode token and extract user data
    return user_data  # You can now use this user data throughout your routes
