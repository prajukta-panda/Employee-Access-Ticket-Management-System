
from getpass import getpass

from database import SessionLocal
from models import User
from enums import UserRole
from utils import get_password_hash


db = SessionLocal()

try:
    existing_admin = (
        db.query(User)
        .filter(User.role == UserRole.ADMIN)
        .first()
    )

    if existing_admin:
        print("An admin account already exists.")

    else:
        name = input("Admin name: ").strip()
        email = input("Admin email: ").strip().lower()
        password = getpass("Admin password: ")
        confirm_password = getpass("Confirm password: ")

        if not name or not email or not password:
            print("Name, email, and password are required.")

        elif password != confirm_password:
            print("Passwords do not match.")

        elif len(password) < 12:
            print("Password must be at least 12 characters.")

        elif db.query(User).filter(User.email == email).first():
            print("This email is already registered.")

        else:
            admin = User(
                name=name,
                email=email,
                password_hash=get_password_hash(password),
                role=UserRole.ADMIN,
                is_active=True,
            )

            db.add(admin)
            db.commit()

            print("Admin account created successfully.")

except Exception:
    db.rollback()
    raise

finally:
    db.close()
