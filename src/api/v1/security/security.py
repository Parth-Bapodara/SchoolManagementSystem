from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from Database.database import get_db
from src.api.v1.user.models.user_models import User
from src.api.v1.utils.response_utils import Response
import logging

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        if not credentials or credentials.scheme != "Bearer":
            return Response(status_code=403, message="Invalid authentication scheme.", data={}).send_error_response()
        
        print(f"Received Token: {credentials.credentials}")

        if not self.verify_jwt(credentials.credentials):
            return Response(status_code=403, message="Invalid or expired token.", data={}).send_error_response()
        
        return credentials.credentials
    
    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            decode_access_token(jwtoken)
            return True
        except HTTPException:
            return False

# Function to create JWT access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()

    if "user_id" not in to_encode:
        return Response(status_code=400, message="User ID is required in the data", data={}).send_error_response()

    expire = datetime.now(timezone.utc).replace(tzinfo=None) + expires_delta if expires_delta else datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=15)
    to_encode.update({"sub": str(data["user_id"]), "exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Decoding the token and extracting the necessary details
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
        if "sub" not in payload:
            return Response(status_code=401, message="Token does not have the required user information.", data={}).send_error_response()
        
        user_id = int(payload["sub"])  
        print(f"Decoded Token User ID: {user_id}")  

        expiration_time = datetime.fromtimestamp(payload["exp"])
        logger.info(expiration_time)
        if expiration_time < datetime.now(timezone.utc).replace(tzinfo=None):
            return Response(status_code=401, message="Token has expired", data={}).send_error_response()
        return payload 

    except JWTError:
        return Response(status_code=401, message="Invalid or expired token", data={}).send_error_response()

# Password hashing and verification functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#used to hash the password received from user
def get_password_hash(password):
    return pwd_context.hash(password)

# Role-based authorization for admin access
def authorize_admin(token: str = Depends(JWTBearer()), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload.get("role") != "admin":
        return Response(status_code=403, message="Admin authorization required", data={}).send_error_response()
    return payload

# Role-based authorization for user access (admin, teacher, student)
def authorize_user(token: str = Depends(JWTBearer()), db: Session = Depends(get_db)):
    """
    Function to authorize the user by validating the JWT token.
    The `sub` claim in the token should contain the username or user ID.
    """
    payload = decode_access_token(token)
    username = payload.get("sub")
    
    if not username:
        return Response(status_code=401, message="Token does not have the required user information.", data={}).send_error_response()
    
    user = db.query(User).filter(User.username == username).first() 

    if not user:
        return Response(status_code=401, message="User not found", data={}).send_error_response()
    
    if user.role not in ["admin", "teacher", "student"]:
        return Response(status_code=403, message="Invalid role", data={}).send_error_response()
    
    return user

# Response format for token responses
def token_response(token: str):
    return {
        "access_token": token,
        "token_type": "bearer"
    }

def get_current_user(token: str = Depends(JWTBearer()), db: Session = Depends(get_db)):
    """
    This function will decode the JWT token and fetch the user from the database
    based on the decoded token (using the 'sub' claim).
    """
    payload = decode_access_token(token)

    userid = payload.get("sub")
    if not userid:
        return Response(status_code=401, message="Token does not have the required user information.", data={}).send_error_response()
    
    user = db.query(User).filter(User.id == userid).first()
    print(user)

    if not user:
        return Response(status_code=401, message="User not found", data={})
    
    return user

async def get_logged_user(token: str = Depends(JWTBearer()), db: Session = Depends(get_db)):
    """
    Decodes the JWT token and returns the user data.
    """
    try:
        user_data = decode_access_token(token)
    except:
        return Response(status_code=403, message="The token is Expired.Generate a new one and try again.")
    
    return user_data 
