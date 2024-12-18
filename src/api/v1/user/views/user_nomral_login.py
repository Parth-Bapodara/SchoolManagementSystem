from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.api.v1.utils.response_utils import Response
from src.api.v1.user.services.Login.normal_login import LoginServices
from Database.database import get_db
from src.api.v1.security.security import JWTBearer

router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user using username/email and password
    """
    return LoginServices.authenticate_user(db, form_data.username, form_data.password)

# Google Login
@router.get("/login/google", summary="Login with Google", description="Redirects the user to the Google Login page.\n\n**Select the link below to login with Google:**\n\n[Login with Google](http://127.0.0.1:8000/login/google)")
async def google_login(request: Request):
    """
    Initiates the Google OAuth2 login flow.
    """
    return await LoginServices.google_login(request)

@router.get("/google/callback", summary="Google Callback", description="Handles the Google OAuth2 callback and token exchange.")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handles the Google OAuth2 callback and fetches user data.
    """
    return await LoginServices.google_callback(request, db)

#Check if the user from login is new or old.
@router.get("/protected-endpoint")
async def protected_endpoint(token: str = Depends(JWTBearer()), db: Session = Depends(get_db)):
    """
    A secured endpoint that verifies the JWT token and checks if the user exists.
    If the user doesn't exist, they are created as a new user.
    """
    response = LoginServices.verify_token_and_get_user(db, token)
    return response

#Facebook Login
@router.get("/login/facebook", summary="Login with Facebook", description="Redirects the user to the Facebook Login page.\n\n**Select the link below to login with facebook:**\n\n[Login with Facebook](http://localhost:8000/login/facebook)")
async def facebook_login(request:Request):
    """
    Initiates the Google OAuth2 login flow.
    """
    return await LoginServices.facebook_login(request)

@router.get("/facebook/callback", summary="Facebook Callback", description="Handles the Facebook OAuth2 callback and token exchange.")
async def facebook_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handles the Google OAuth2 callback and fetches user data.
    """
    return await LoginServices.facebook_callback(request, db)