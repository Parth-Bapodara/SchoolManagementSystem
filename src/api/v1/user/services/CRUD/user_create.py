from fastapi import FastAPI, Depends, HTTPException, status, Request, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.api.v1.user.schemas.user_schemas import UserCreate, UserInDb, UserUpdate
from src.api.v1.authentication import security
from src.api.v1.user.models.user_models import User
from Database.database import get_db, Base, engine
from jose import jwt, JWTError
from src.api.v1.authentication.security import oauth2_scheme

router = APIRouter()
Base.metadata.create_all(bind=engine)

@router.post("/user/create/")
def create_user(user: UserCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    if user_data["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create new users."
        )

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists.")

    hashed_password = security.get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        username=user.username,
        status="active"  
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"msg": f"{user.role.capitalize()} created successfully", "email": db_user.email, "id": db_user.id}
