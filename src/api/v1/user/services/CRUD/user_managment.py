from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.api.v1.user.models.user_models import User
from src.api.v1.security import security
from fastapi import HTTPException, status
from src.api.v1.utils.response_utils import Response
from src.api.v1.user.schemas.user_schemas import UserCreate, UserUpdate
from jose import jwt, JWTError

class UserServices:

    @staticmethod
    def create_user(db: Session, user_data: UserCreate, token: str):
        try:
            user_data_decoded = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        except JWTError:
            return Response(status_code=403, message="Could not validate credentials", data={}).send_error_response()

        if user_data_decoded["role"] != "admin":
            return Response(
                status_code=403,
                message="Only admins can create new users.",
                data={}
            ).send_error_response()

        existing_user = db.query(User).filter(or_(User.email == user_data.email, User.username == user_data.username)).first()

        if existing_user:
            if existing_user.email == user_data.email:
                return Response(status_code=400, detail="Email already in use.", data={}).send_error_response()
            elif existing_user.username == user_data.username:
                return Response(status_code=400, message="Username already in use.", data={}).send_error_response()
            # return Response(status_code=400, message="User already exists.", data={}).send_error_response()

        hashed_password = security.get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role,
            username=user_data.username,
            status="active"
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {"msg": f"{user_data.role.capitalize()} created successfully", "email": db_user.email, "id": db_user.id, "role": db_user.role}

    @staticmethod
    def update_user_info(db: Session, user_update: UserUpdate, token: str):
        try:
            user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        except JWTError:
            return Response(status_code=403, message="Could not validate credentials", data={}).send_error_response()

        user_id = int(user_data.get("user_id"))
        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user:
            return Response(status_code=404, message="User not found.", data={}).send_error_response()

        if user_update.password:
            current_user.hashed_password = security.get_password_hash(user_update.password)

        db.commit()
        db.refresh(current_user)

        return current_user

    @staticmethod
    def get_users_by_role(db: Session, token: str, role: str, page: int, limit: int):
        try:
            user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        except JWTError:
            return Response(status_code=403, message="Could not validate credentials", data={}).send_error_response()

        if user_data["role"] != "admin":
            return Response(
                status_code=403,
                message="Not authorized to view users.",
                data={}
            ).send_error_response()
        
        skip = (page - 1) * limit

        users = db.query(User).filter(User.role == role).offset(skip).limit(limit).all()
        total_users = db.query(User).filter(User.role == role).count()

        if not users:
            if skip >= total_users:
                return Response(status_code=404, message="Page exceeds the number of available users.", data={}).send_error_response()
            return Response(status_code=404, message=f"No {role}s found.", data={}).send_error_response()

        total_pages = (total_users + limit - 1) // limit

        return {
            "page": page,
            "limit": limit,
            "total_users": total_users,
            "total_pages": total_pages,
            "users": users
        }

    @staticmethod
    def get_user_info(db: Session, token: str):
        try:
            user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        except JWTError:
            return Response(status_code=403, message="Could not validate credentials", data={}).send_error_response()

        user_id = int(user_data.get("user_id"))
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return Response(status_code=404, message="User not found.", data={})
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int, token: str):
        try:
            user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        except JWTError:
            return Response(status_code=403, detail="Could not validate credentials", data={}).send_error_response()

        if user_data["role"] != "admin":
            return Response(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete users.", data={}).send_error_response()

        user_to_delete = db.query(User).filter(User.id == user_id).first()
        if not user_to_delete:
            return Response(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.", data={}).send_error_response()

        db.delete(user_to_delete)
        db.commit()

        return{"msg": "User deleted successfully"}
