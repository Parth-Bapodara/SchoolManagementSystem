from app.database import SessionLocal, engine
from app.models import User
from app.auth.auth_handler import hash_password
from app.database import Base

Base.metadata.create_all(bind=engine)

admin_email = "admin@example.com"
admin_password = "Admin@1234"  
admin_first_name = "Admin"
admin_last_name = "User"
admin_role = "admin"

db = SessionLocal()
try:
    if not db.query(User).filter(User.email == admin_email).first():
        new_admin = User(
            email=admin_email,
            f_name=admin_first_name,
            l_name=admin_last_name,
            role=admin_role,
            password=hash_password(admin_password)
        )
        db.add(new_admin)
        db.commit()
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")
finally:
    db.close()