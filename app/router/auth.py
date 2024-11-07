from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from app import schemas, models, database
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login")
async def login(form_data:OAuth2PasswordRequestForm = Depends(), db:Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username, "role":user.role})
    return {"access_token": access_token, "token_type": "bearer"}

    
# @router.post("/auth/admin/login")
# async def authenticate_admin(
#     username: str,
#     password: str,
#     db: Session = Depends(database.get_db)
# ):
#     admin = db.query(Admin).filter(Admin.username == username).first()

#     if admin is None or not verify_password(password, admin.hashed_password):
#         raise HTTPException(status_code=400, detail="Invalid credentials")

#     access_token = create_access_token(data={"sub": admin.username, "role": "admin"})
#     return {"access_token": access_token, "token_type": "bearer"}

# async def get_current_user(token: str = Depends(oauth2scheme), db:Session=Depends(database.get_db)):
#     payload = decode_access_token(token)
#     username = payload.get("sub")
#     role = payload.get("role")
#     if not username or not role:
#         raise HTTPException(status_code=401, detail="Invalid token")
    
#     user = db.query(Admin).filter(Admin.username == username).first()
#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")
#     return user