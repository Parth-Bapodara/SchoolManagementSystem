from authlib.integrations.starlette_client import OAuth
from Config.config import settings

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",  
    access_token_url="https://oauth2.googleapis.com/token",
    refresh_token_url=None,
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration", 
    redirect_uri="http://127.0.0.1:8000/google/callback"
)
