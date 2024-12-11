from fastapi import HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from google.auth.transport.requests import Request
from src.api.v1.user.models.user_models import User
from src.api.v1.security import security
from src.api.v1.utils.response_utils import Response
from sqlalchemy.exc import IntegrityError
from src.api.v1.user.utils.google_auth import oauth
from src.api.v1.user.utils.facebook_auth import oauth_1
#from src.api.v1.user.utils.apple_auth import oauth_apple
import logging
from src.api.v1.security.security import get_password_hash

class LoginServices:

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        """
        Authenticate a user based on the provided username and password.
        """
        user = db.query(User).filter(User.email == username).first() or db.query(User).filter(User.username == username).first()

        if not user or not security.verify_password(password, user.hashed_password):
            return Response(status_code=401, message="Incorrect username or password", data={}).send_error_response()
        
        user_data = {"user_id": user.id, "role": user.role, "Mail": user.email, "Username": user.username, "Status": user.status, "Mobile_no": user.mobile_no}
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
        redirect_uri = "http://127.0.0.1:8000/google/callback"  
        return await oauth.google.authorize_redirect(request, redirect_uri)
    
    @staticmethod
    async def google_callback(request: Request, db: Session):
        """
        This endpoint handles the Google OAuth2 callback.
        It receives the authorization code, exchanges it for an access token,
        and retrieves user info from Google.
        """
        try:
            token = await oauth.google.authorize_access_token(request)
            
            user_info = await oauth.google.get("https://www.googleapis.com/oauth2/v3/userinfo", token=token)

            if user_info.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch user information from Google.")
            
            user_data = user_info.json()
            user_email = user_data['email']
            username = user_data.get('name', user_email) 

            user = db.query(User).filter(User.email == user_email).first()

            if user:
                user_data = {"user_id": user.id, "role": user.role, "Mail": user.email, "Username": user.username, "Status": user.status}
                access_token = security.create_access_token(data=user_data)
                return Response(status_code=200, message="User already exists, proceeding", data={
                    "access_token": access_token,
                    "token_type": "bearer",
                    "User_Data": user_data
                }).send_success_response()

            hashed_password = get_password_hash("Test@123")
            new_user = User(
                email=user_email,
                username=username, 
                hashed_password=hashed_password,
                role="student", 
                status="active",
            )
            db.add(new_user)
            try:
                db.commit() 
            except IntegrityError:
                db.rollback()
                raise HTTPException(status_code=400, detail="Error creating user, possibly a duplicate.")
            
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
                    mobile_no="911234567890"
                )
                db.add(new_user)
                db.commit()

                user_data = {
                    "user_id": new_user.id, 
                    "role": new_user.role, 
                    "email": new_user.email, 
                    "username": new_user.username, 
                    "status": new_user.status,
                    "mobile_no": new_user.mobile_no
                }
                access_token = security.create_access_token(data=user_data)

                return {"message": "New user created", "user": new_user, "access_token": access_token}
            
            user_data = {
                "user_id": user.id, 
                "role": user.role, 
                "email": user.email, 
                "username": user.username, 
                "status": user.status,
                "mobile_no": user.mobile_no
            }
            access_token = security.create_access_token(data=user_data)

            return {"message": "User already exists", "user": user, "access_token": access_token}

        except Exception:
            return Response(status_code=401, message="Invalid or expired token", data={}).send_error_response()

    @staticmethod
    async def facebook_login(request: Request):
        """
        Initiates the Facebook OAuth2 login flow.
        This method will redirect the user to GFacebook's OAuth2 page for authentication.
        """
        redirect_uri = "http://localhost:8000/facebook/callback"
        return await oauth_1.facebook.authorize_redirect(request, redirect_uri)
    
    @staticmethod
    async def facebook_callback(request: Request, db:Session):
        try:
            token = await oauth_1.facebook.authorize_access_token(request)
            
            user_info = await oauth_1.facebook.get("https://graph.facebook.com/me?fields=id,name,email", token=token)

            if user_info.status_code != 200:
                logging("data fetched successfully")
                return Response(status_code=400, message="Failed to fetch user information from Facebook.", data={}).send_error_response()
            
            user_data = user_info.json()
            user_email = user_data['email']
            username = user_data.get('name', user_email) 

            user = db.query(User).filter(User.email == user_email).first()

            if user:
                user_data = {"user_id": user.id, "role": user.role, "Mail": user.email, "Username": user.username, "Status": user.status}
                access_token = security.create_access_token(data=user_data)
                return Response(status_code=200, message="User already exists, proceeding", data={
                    "access_token": access_token,
                    "token_type": "bearer",
                    "User_Data": user_data
                }).send_success_response()
            
            hashed_password = get_password_hash("Test@123")
            print(hashed_password)
            new_user = User(
                email=user_email,
                username=username, 
                hashed_password=hashed_password,
                role="student", 
                status="active",
            )
            db.add(new_user)
            try:
                db.commit() 
            except IntegrityError:
                db.rollback()
                return Response(status_code=400, message="Error creating user, possibly a duplicate.", data={}).send_error_response()
            
            user_data = {"user_id": new_user.id, "role": new_user.role, "Mail": new_user.email, "Username": new_user.username, "Status": new_user.status}
            access_token = security.create_access_token(data=user_data)

            return Response(status_code=200, message="Facebook Login successful, new user created", data={
                "access_token": access_token,
                "token_type": "bearer",
                "User_Data": user_data
            }).send_success_response()

        except Exception as e:
            return Response(status_code=400, message=f"Error occurred during Facebook login: {str(e)}", data={}).send_error_response()

    @staticmethod
    async def apple_login(request: Request):
        """
        Initiates the Apple OAuth2 login flow.
        This method will redirect the user to Apple's OAuth2 page for authentication.
        """
        redirect_uri = "http://127.0.0.1:8000/apple/callback"
        return await oauth_apple.apple.authorize_redirect(request, redirect_uri)
    
    @staticmethod
    async def apple_callback(request: Request):
        try:
            token = await oauth_1.facebook.authorize_access_token(request)
            
            user_info = await oauth_1.facebook.get("https://graph.facebook.com/me?fields=id,name,email", token=token)

            if user_info.status_code != 200:
                logging("data fetched successfully")
                return Response(status_code=400, message="Failed to fetch user information from Facebook.", data={}).send_error_response()
        except Exception as e:
            return Response(status_code=400, message=f"Error occurred during Apple login: {str(e)}", data={}).send_error_response()
