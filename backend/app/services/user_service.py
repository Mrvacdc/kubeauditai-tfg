from sqlalchemy.orm import Session

from app.models.user import User
from app.security.passwords import (
    hash_password,
    verify_password,
    validate_password_policy,
)



def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def create_user(
    db: Session,
    full_name: str,
    email: str,
    password: str,
    role: str = "SECURITY",
) -> User:
    existing_user = get_user_by_email(db, email)

    if existing_user:
        raise ValueError("User already exists")

    validate_password_policy(password)

    user = User(
        full_name=full_name,
        email=email,
        role=role,
        password_hash=hash_password(password),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
