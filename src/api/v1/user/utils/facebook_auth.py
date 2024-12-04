from authlib.integrations.starlette_client import OAuth
from Config.config import settings

oauth_1 = OAuth()

oauth_1.register(
    name="facebook",
    client_id=settings.FACEBOOK_CLIENT_ID,
    client_secret=settings.FACEBOOK_CLIENT_SECRET,
    authorize_url="https://www.facebook.com/dialog/oauth",  
    access_token_url="https://graph.facebook.com/v21.0/oauth/access_token",
    refresh_token_url=None,
    client_kwargs={"scope": "email,public_profile"},
    api_base_url='https://graph.facebook.com/',
    redirect_uri="http://localhost:8000/facebook/callback"
)
