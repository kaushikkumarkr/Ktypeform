from app.core.db import SessionLocal
from app.models.user import User, Organization, UserRole
from app.core.security import get_password_hash

def seed():
    db = SessionLocal()
    try:
        # 1. Create Organization
        org = db.query(Organization).filter(Organization.name == "Demo Org").first()
        if not org:
            org = Organization(name="Demo Org", tier="pro")
            db.add(org)
            db.commit()
            db.refresh(org)
            print(f"Created Organization: {org.name}")
        else:
            print(f"Organization exists: {org.name}")

        # 2. Create User
        email = "admin@example.com"
        password = "password"
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                is_active=True,
                role=UserRole.ADMIN,
                org_id=org.id
            )
            db.add(user)
            db.commit()
            print(f"Created User: {email} / {password}")
        else:
            print(f"User exists: {email}")

    except Exception as e:
        print(f"Error seeding DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
