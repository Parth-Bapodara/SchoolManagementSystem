# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.auth.auth_handler import get_password_hash,verify_password, create_access_token, decode_token, oauth2_scheme
# from app.schemas import AdminSchema, UserSchema, AdminLoginSchema, UserLogin
# from app.database import get_db
# from app.models import Admin, User

# router = APIRouter()

# @router.post("/admin/signup")
# async def admin_signup(admin: AdminSchema, db: Session = Depends(get_db)):
#     db_admin = db.query(Admin).filter(Admin.email == admin.email).first()
#     if db_admin:
#         raise HTTPException(status_code = 400, detail="Admin Already exists")
    
#     hashed_password = get_password_hash(admin.password)
#     new_admin = Admin(email=admin.email, f_name = admin.f_name, l_name = admin.l_name, password=hashed_password)
#     db.add(new_admin)
#     db.commit()
#     db.refresh(new_admin)
#     return {"msg": "Admin account created successfully"}

# @router.post("/admin/login")
# async def admin_login(admin: AdminLoginSchema, db: Session = Depends(get_db)):
#     db_admin = db.query(Admin).filter(Admin.email == admin.email).first()
#     if not db_admin or not verify_password(admin.password, db_admin.password):
#         raise HTTPException(status_code=401, detail="Invalid Credentials")
    
#     access_token = create_access_token(data={"sub": admin.email})
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.post("/admin/create-user")
# async def create_user(user: UserSchema, token: str = Depends(oauth2_scheme), db:Session = Depends(get_db)):
#     payload = decode_token(token)
#     admin_email = payload.get("sub")

#     if not db.query(Admin).filter(Admin.email == admin_email).first():
#         raise HTTPException(status_code=403, detail="Not authorized to create users")
    
#     hashed_password = get_password_hash(user.password)
#     new_user = User(email=user.email, f_name = user.f_name, l_name = user.l_name, role=user.role, password = hashed_password)
#     db.add(new_user)
#     db.commit()
#     return{"msg": f"{user.role.capitalize()} created successfully"}

# @router.post("/user/login")
# async def user_login(user: UserLogin, db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.email == user.email).first()
#     if not db_user or not verify_password(user.password, db_user.password):
#         raise HTTPException(status_code=401, detail="Invalid Credentials")
    
#     access_token = create_access_token(data={"sub": user.email})
#     return {"access_token": access_token, "token_type": "bearer"}
