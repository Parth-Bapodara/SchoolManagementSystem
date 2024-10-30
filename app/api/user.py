from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.auth_handler import verify_password, create_access_token, decode_token, hash_password, oauth2_scheme
from app.database import get_db
from app.models import User
from app.schemas import UserSchema, UserLogin

router = APIRouter(prefix="/user")

@router.post("/create-user")
async def create_user(user:UserSchema, db:Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, f_name=user.f_name, l_name=user.l_name, role=user.role, password=hashed_password)
    db.add(new_user)
    db.commit()
    return{"msg": f"{user.role.capitalize()} created successfully"}

@router.post("/login")
async def login(user:UserLogin,form_data:OAuth2PasswordRequestForm = Depends()):
     db_user = db.query(User).filter(User.email == form_data.username).first()
     if not db_user or not verify_password(form_data.password, db_user.password):
         raise HTTPException(status_code=401, detail="Invalid Credentials")
    
     access_token = create_access_token(data={"sub": db_user.email, "role":db_user.role})
     return{"access_token": access_token, "token_type":"bearer"}

@router.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    return{"msg": "You are authorized", "user":payload}
