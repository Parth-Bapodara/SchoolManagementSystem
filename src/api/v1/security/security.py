from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from Database.database import get_db
from src.api.v1.user.models.user_models import User

# Secret key for encoding/decoding JWT tokens, store it securely
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context for bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer Authentication
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        if not credentials or credentials.scheme != "Bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
        
        # Log the received token for debugging
        print(f"Received Token: {credentials.credentials}")

        # Verify the JWT token
        if not self.verify_jwt(credentials.credentials):
            raise HTTPException(status_code=403, detail="Invalid or expired token.")
        
        return credentials.credentials
    
    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            # Decode and validate the token
            decode_access_token(jwtoken)
            return True
        except HTTPException:
            return False

# Function to create JWT access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()

    # Ensure 'user_id' is included (this is now the subject)
    if "user_id" not in to_encode:
        raise HTTPException(status_code=400, detail="User ID is required in the data")

    expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"sub": str(data["user_id"]), "exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Decoding the token and extracting the necessary details
def decode_access_token(token: str):
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract user_id from the 'sub' field in the payload (ensure it's an integer)
        if "sub" not in payload:
            raise HTTPException(status_code=401, detail="Token does not have the required user information.")
        
        user_id = int(payload["sub"])  # Ensure user_id is treated as an integer
        print(f"Decoded Token User ID: {user_id}")  # Debugging: Print the user_id

        # Verify if the token is expired
        expiration_time = datetime.utcfromtimestamp(payload["exp"])
        if expiration_time < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token has expired")

        return payload  # Return the decoded payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# Password hashing and verification functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Role-based authorization for admin access
def authorize_admin(token: str = Depends(JWTBearer()), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin authorization required")
    return payload

# Role-based authorization for user access (admin, teacher, student)
def authorize_user(token: str = Depends(JWTBearer()), db: Session = Depends(get_db)):
    """
    Function to authorize the user by validating the JWT token.
    The `sub` claim in the token should contain the username or user ID.
    """
    # Decode the access token to get user data
    payload = decode_access_token(token)
    
    username = payload.get("sub")  # 'sub' should contain the username (or user ID)
    
    # If the 'sub' field is not set or is invalid, raise an error
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token does not have the required user information.")
    
    # Fetch user details from the database using the username (or user_id)
    user = db.query(User).filter(User.username == username).first()  # You can use 'user_id' instead of 'username' if preferred
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    # Ensure the role is valid by checking the user's role from the database
    if user.role not in ["admin", "teacher", "student"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid role")
    
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
    
    # Extract the 'sub' claim (which should be the username)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Token does not have the required user information.")
    
    # Fetch the user from the database using the username
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
