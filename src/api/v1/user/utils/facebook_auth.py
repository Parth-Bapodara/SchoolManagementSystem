from authlib.integrations.starlette_client import OAuth
from Config.config import settings

oauth = OAuth()

oauth.register(
    name="facebook",
    client_id=settings.FACEBOOK_CLIENT_ID,
    client_secret=settings.FACEBOOK_CLIENT_SECRET,
    authorize_url="https://www.facebook.com/dialog/oauth",  
    access_token_url="https://graph.facebook.com/oauth/access_token",
    refresh_token_url=None,
    client_kwargs={"scope": "email"},
    api_base_url='https://graph.facebook.com/', 
    redirect_uri="https://127.0.0.1:8000/facebook/callback"
)
