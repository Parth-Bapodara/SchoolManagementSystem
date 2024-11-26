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

@router.put("/update-info/", response_model=UserInDb)
async def update_user_info(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        user_data = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    user_id = int(user_data.get("user_id"))
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user_update.password:
        current_user.hashed_password = security.get_password_hash(user_update.password)

    db.commit()
    db.refresh(current_user)

    return current_user
