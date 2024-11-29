from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from google.auth.transport.requests import Request
import google.auth
from src.api.v1.user.models.user_models import User
from src.api.v1.security import security
from src.api.v1.utils.response_utils import Response
from sqlalchemy.exc import IntegrityError
from src.api.v1.user.utils.google_auth import oauth
import logging

class LoginServices:

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        """
        Authenticate a user based on the provided username and password.
        """
        user = db.query(User).filter(User.email == username).first() or db.query(User).filter(User.username == username).first()

        if not user or not security.verify_password(password, user.hashed_password):
            return Response(status_code=401, message="Incorrect username or password", data={}).send_error_response()
        
        user_data = {"user_id": user.id, "role": user.role, "Mail": user.email, "Username": user.username, "Status": user.status}
        access_token = security.create_access_token(data=user_data)

        return Response(status_code=200, message="Login successful", data={
            "access_token": access_token, 
            "token_type": "bearer", 
            "User_Data": user_data
        }).send_success_response()

    @staticmethod
    async def google_login(request: Request):
        """
        Initiates the Google OAuth2 login flow.
        This method will redirect the user to Google's OAuth2 page for authentication.
        """
        redirect_uri = "http://127.0.0.1:8000/google/callback"  # URL where Google will send the response
        return await oauth.google.authorize_redirect(request, redirect_uri)

    @staticmethod
    async def google_callback(request: Request, db: Session):
        """
        This endpoint handles the Google OAuth2 callback.
        It receives the authorization code, exchanges it for an access token,
        and retrieves user info from Google.
        """
        try:
            # Exchange the authorization code for a token
            token = await oauth.google.authorize_access_token(request)
            
            # Get the user information from Google API
            user_info = await oauth.google.get("https://www.googleapis.com/oauth2/v3/userinfo", token=token)

            if user_info.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch user information from Google.")
            
            user_data = user_info.json()
            user_email = user_data['email']
            username = user_data.get('name', user_email)  # Use Google username or email if no name

            # Check if the user exists in the database
            user = db.query(User).filter(User.email == user_email).first()

            if user:
                # If user already exists, return success response with token
                user_data = {"user_id": user.id, "role": user.role, "Mail": user.email, "Username": user.username, "Status": user.status}
                access_token = security.create_access_token(data=user_data)
                return Response(status_code=200, message="User already exists, proceeding", data={
                    "access_token": access_token,
                    "token_type": "bearer",
                    "User_Data": user_data
                }).send_success_response()

            # If the user doesn't exist, create a new user with Google data
            new_user = User(
                email=user_email,
                username=username,  # Set Google username as the default
                role="student",  # Set default role as 'student'
                status="active",  # Default status is active
            )

            # Add user to the database and commit the transaction
            db.add(new_user)
            try:
                db.commit()  # Commit the transaction
            except IntegrityError:
                db.rollback()  # If there’s an integrity error (e.g., duplicate username), rollback the transaction
                raise HTTPException(status_code=400, detail="Error creating user, possibly a duplicate.")
            
            # Generate a JWT token for the new user
            user_data = {"user_id": new_user.id, "role": new_user.role, "Mail": new_user.email, "Username": new_user.username, "Status": new_user.status}
            access_token = security.create_access_token(data=user_data)

            return Response(status_code=200, message="Google Login successful, new user created", data={
                "access_token": access_token,
                "token_type": "bearer",
                "User_Data": user_data
            }).send_success_response()

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error occurred during Google login: {str(e)}")

    @staticmethod
    def verify_token_and_get_user(db: Session, token: str):
        """
        Verifies the JWT token, decodes it, and returns the user information.
        If the user does not exist, create a new user and return the user info.
        Also generates a new access token.
        """
        try:
            payload = security.decode_access_token(token)
            user_id = payload.get("user_id")

            if not user_id:
                raise HTTPException(status_code=401, detail="Token is missing 'user_id'")

            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                user_email = payload.get("Mail")
                username = payload.get("Username")
                
                if not user_email or not username:
                    raise HTTPException(status_code=400, detail="Missing user email or username in token")
                
                new_user = User(
                    email=user_email,
                    username=username,  
                    role="student",  
                    status="active",  
                )
                db.add(new_user)
                db.commit()

                user_data = {
                    "user_id": new_user.id, 
                    "role": new_user.role, 
                    "email": new_user.email, 
                    "username": new_user.username, 
                    "status": new_user.status
                }
                access_token = security.create_access_token(data=user_data)

                return {"message": "New user created", "user": new_user, "access_token": access_token}
            
            user_data = {
                "user_id": user.id, 
                "role": user.role, 
                "email": user.email, 
                "username": user.username, 
                "status": user.status
            }
            access_token = security.create_access_token(data=user_data)

            return {"message": "User already exists", "user": user, "access_token": access_token}

        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")



