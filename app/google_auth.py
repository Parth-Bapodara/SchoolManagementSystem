from authlib.integrations.starlette_client import OAuth
from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

oauth = OAuth()

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    access_token_url="https://oauth2.googleapis.com/token",
    refresh_token_url=None,
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration"
)