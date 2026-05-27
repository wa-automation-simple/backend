"""User repository for database operations."""

from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional, List, Tuple
from datetime import datetime

from auth.models.user import User, UserRole
from auth.core.security import get_password_hash


class UserRepository:
    """Repository for User model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, username: str, email: str, password: str, role: UserRole = UserRole.USER) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(password)
        
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user fields."""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        # Update updated_at timestamp
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user_id: int) -> bool:
        """Delete a user."""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def list_users(
        self, 
        page: int = 1, 
        page_size: int = 20,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """List users with pagination and filters."""
        query = select(User)
        
        if role:
            query = query.where(User.role == role)
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        users = self.db.execute(query).scalars().all()
        return list(users), total
    
    def update_last_login(self, user_id: int) -> Optional[User]:
        """Update user's last login timestamp."""
        return self.update(user_id, last_login=datetime.utcnow())
    
    def verify_user(self, user_id: int) -> Optional[User]:
        """Mark user as verified."""
        return self.update(user_id, is_verified=True)
