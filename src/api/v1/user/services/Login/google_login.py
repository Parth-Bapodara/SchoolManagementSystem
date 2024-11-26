from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from src.api.v1.authentication.google_auth import oauth
from src.api.v1.authentication.security import JWTBearer, create_access_token, decode_access_token, token_response
from datetime import timedelta
from starlette.middleware.sessions import SessionMiddleware
from Config import config

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/login/google", summary="Login with Google", description="Redirects the user to the Google Login page.\n\n**Select the link below to login with Google:**\n\n[Login with Google](http://127.0.0.1:8000/login/google)")
async def google_login(request: Request):
    """
    Redirect the user to Google OAuth2 for authentication.
    This will redirect to Google's login page.
    """
    redirect_uri = "http://127.0.0.1:8000/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request):
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

        internal_data = {"sub": user_data["email"], "user_id": user_data["sub"]}
        access_token = create_access_token(internal_data, expires_delta=timedelta(minutes=30))

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error occurred: {str(e)}")

@router.get("/protected-endpoint")
async def protected_endpoint(token: str = Depends(JWTBearer())):
    """
    A secured endpoint that requires a valid JWT token.
    """
    try:
        payload = decode_access_token(token)
        return {"message": "Token is valid", "payload": payload}
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")



