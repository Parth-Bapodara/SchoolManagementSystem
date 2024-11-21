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
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    user = db.query(User).filter(User.email == user_info["email"]).first()

    if user_info:
        email = user_info.get("email")
        name = user_info.get("name")
    
        if email and name:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                # user = User(email=email, username=name)
                # db.add(user)
                # db.commit()
                pass    
            return {"message": "Login successful", "user": {"email": email, "name": name}}
        else:
            raise HTTPException(status_code=400, detail="Invalid user info")
    else:
        raise HTTPException(status_code=400, detail="No user info found in the token")





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
