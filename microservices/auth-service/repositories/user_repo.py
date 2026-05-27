"""User repository for Auth Service."""
from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.user import User, UserRole
from datetime import datetime


class UserRepository:
    """Repository for user database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, email: str, username: str, password_hash: str, 
               full_name: Optional[str] = None, role: UserRole = UserRole.USER) -> User:
        """Create a new user."""
        user = User(
            email=email,
            username=username,
            password_hash=password_hash,
            full_name=full_name,
            role=role
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def list_users(self, skip: int = 0, limit: int = 100, 
                   is_active: Optional[bool] = None,
                   role: Optional[UserRole] = None) -> List[User]:
        """List users with pagination and filters."""
        query = self.db.query(User)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        if role is not None:
            query = query.filter(User.role == role)
        
        return query.offset(skip).limit(limit).all()
    
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user fields."""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user_id: int) -> bool:
        """Delete user."""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def update_last_login(self, user_id: int) -> Optional[User]:
        """Update last login timestamp."""
        return self.update(user_id, last_login=datetime.utcnow())
    
    def verify_user(self, user_id: int) -> Optional[User]:
        """Verify user account."""
        return self.update(user_id, is_verified=True)
