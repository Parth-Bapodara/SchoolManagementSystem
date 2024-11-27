from fastapi import FastAPI, Depends, HTTPException, status, Request, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.api.v1.security import security
from src.api.v1.user.models.user_models import User
from Database.database import get_db, Base, engine
from jose import jwt, JWTError
from src.api.v1.security.security import oauth2_scheme

router = APIRouter()
Base.metadata.create_all(bind=engine)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first() or db.query(User).filter(User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_data = {"user_id": user.id, "role": user.role, "Mail":user.email, "Username":user.username, "Status": user.status}
    access_token = security.create_access_token(data=user_data)

    # access_token = security.create_access_token(data={"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "User_Data": user_data}