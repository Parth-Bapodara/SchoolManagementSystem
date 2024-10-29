from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.auth_handler import verify_password, create_access_token, oauth2_scheme, decode_token
from app.database import get_db
from app.models import Admin, User
from app.schemas import AdminSchema, UserSchema, AdminLoginSchema, UserLogin
from app.utils.hashing import hash_password

router = APIRouter(prefix="/admin")

@router.post("/signup")
async def admin_signup(admin: AdminSchema, db: Session = Depends(get_db)):
    if db.query(Admin).filter(Admin.email == admin.email).first():
        raise HTTPException(status_code = 400, detail="Admin Already exists")
    
    hashed_password = hash_password(admin.password)
    new_admin = Admin(email=admin.email, f_name = admin.f_name, l_name = admin.l_name, password=hashed_password)
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return {"msg": "Admin account created successfully"}

@router.post("/login")
async def admin_login(admin: AdminLoginSchema, db: Session = Depends(get_db)):
    db_admin = db.query(Admin).filter(Admin.email == admin.email).first()
    if not db_admin or not verify_password(admin.password, db_admin.password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    access_token = create_access_token(data={"sub": admin.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/create-user")
async def create_user(user: UserSchema, token: str = Depends(oauth2_scheme), db:Session = Depends(get_db)):
    payload = decode_token(token)
    admin_email = payload.get("sub")

    if not db.query(Admin).filter(Admin.email == admin_email).first():
        raise HTTPException(status_code=403, detail="Not authorized to create users")
    
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, f_name = user.f_name, l_name = user.l_name, role=user.role, password = hashed_password)
    db.add(new_user)
    db.commit()
    return{"msg": f"{user.role.capitalize()} created successfully"}