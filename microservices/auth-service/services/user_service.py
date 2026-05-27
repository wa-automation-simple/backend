"""
User Service - Business logic for user management
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from auth_service.models.user import User, UserRole
from shared.security import get_password_hash, verify_password


class UserService:
    """Service layer for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(
        self, 
        username: str, 
        email: str, 
        password: str, 
        role: str = "user"
    ) -> User:
        """Create a new user."""
        # Check if user exists
        existing_user = self.get_user_by_username(username)
        if existing_user:
            raise ValueError("Username already exists")
        
        existing_email = self.get_user_by_email(email)
        if existing_email:
            raise ValueError("Email already registered")
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            role=UserRole(role),
            is_active=True
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        user = self.get_user_by_username(username)
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user fields."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        self.db.commit()
        return True
    
    def list_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """List users with pagination and filters."""
        query = self.db.query(User)
        
        if role:
            query = query.filter(User.role == UserRole(role))
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
