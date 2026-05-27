from sqlalchemy.orm import Session
from typing import Optional
from auth_service.models.user import User
from auth_service.services.auth_service import hash_password, verify_password
from shared.utils.auth import create_access_token
from datetime import timedelta
from shared.config.settings import settings


def create_user(db: Session, email: str, password: str, full_name: str, role: str = "trial") -> User:
    """Create a new user"""
    hashed_password = hash_password(password)
    db_user = User(
        email=email,
        password_hash=hashed_password,
        full_name=full_name,
        role=role,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
    """Update user fields"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user


def generate_token_for_user(user: User) -> str:
    """Generate JWT token for user"""
    return create_access_token(
        data={"sub": user.id, "role": user.role.value},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )
