from app.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def create_admin(email: str, name: str, password: str, phone: str | None = None) -> None:
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError(f"User with email '{email}' already exists.")

        admin = User(
            name=name,
            email=email,
            phone=phone,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"Admin created successfully: {admin.email}")
        print(f"Admin ID: {admin.id}")
        print(f"Role: {admin.role}")
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()


if __name__ == "__main__":
    admin_name = input("Enter admin full name: ").strip()
    admin_email = input("Enter admin email: ").strip()
    admin_password = input("Enter admin password: ").strip()
    admin_phone = input("Enter admin phone (optional, press Enter to skip): ").strip() or None

    create_admin(admin_email, admin_name, admin_password, admin_phone)
