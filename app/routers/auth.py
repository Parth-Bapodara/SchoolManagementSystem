from fastapi import APIRouter, Depends, Request,HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.google_auth import oauth
from app.models import User
from app.database import get_db
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="app/templates") 

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/login/google")
async def google_login(request: Request):
    redirect_uri = "http://127.0.0.1:8000/google/callback"
    print("Redirect_uri:", redirect_uri)
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    print(f"Received code: {code}, (type: {type(code)}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing.")
    
    try:
        token = await oauth.google.fetch_access_token(code=code)
        print(f"Token response: {token}")
        user_info = await oauth.google.get("https://www.googleapis.com/oauth2/v3/userinfo", token=token)
        
        if not user_info.ok:
            raise HTTPException(status_code=400, detail="Failed to fetch user information from Google.")

        user_data = user_info.json() 
        email = user_data.get("email")
        name = user_data.get("name")

        if not email or not name:
            raise HTTPException(status_code=400, detail="Missing email or name in user info.")
        
        user = db.query(User).filter(User.email == email).first()

        if not user:
            # user = User(email=email, name=name)
            # db.add(user)
            # db.commit()
            pass

        return {"message": "Login successful", "user": {"email": email, "name": name}}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error occurred while processing the authorization code: {str(e)}")

# @router.get("/google/callback")
# async def google_callback(request: Request, db: Session = Depends(get_db)):
#     token = await oauth.google.authorize_access_token(request)
#     user_info = token.get("userinfo")

#     if user_info:
#         email = user_info.get("email")
#         name = user_info.get("name")
    
#         if email and name:
#             user = db.query(User).filter(User.email == email).first()
#             if not user:
#                 # user = User(email=email, username=name)
#                 # db.add(user)
#                 # db.commit()
#                 pass    
#             return {"message": "Login successful", "user": {"email": email, "name": name}}
#         else:
#             raise HTTPException(status_code=400, detail="Invalid user info")
#     else:
#         raise HTTPException(status_code=400, detail="No user info found in the token")





# @router.get("/auth/google/callback")
# async def google_callback(request: Request, db: Session = Depends(get_db)):
#     token = await oauth.google.authorize_access_token(request)
#     user_info = await oauth.google.parse_id_token(request, token)
    
#     user = db.query(User).filter(User.email == user_info["email"]).first()
    
#     if not user:
#         user = User(email=user_info["email"], name=user_info["name"])
#         db.add(user)
#         db.commit()

#     return {"message": "Login successful", "user": {"email": user.email}}
