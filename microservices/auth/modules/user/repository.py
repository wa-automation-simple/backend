"""Repository for User database operations."""

from sqlalchemy.orm import Session, selectinload
from typing import Optional, List
from datetime import datetime

from modules.user.model import User


class UserRepository:
    """Repository for User model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== User Operations ====================
    
    def create(self, **kwargs) -> User:
        """Create a new user."""
        item = User(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).options(
            selectinload(User.roles)
        ).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).options(
            selectinload(User.roles)
        ).filter(User.email == email).first()
    
    def get_by_google_sub(self, google_sub: str) -> Optional[User]:
        """Get user by Google subject ID."""
        return self.db.query(User).options(
            selectinload(User.roles)
        ).filter(User.google_sub == google_sub).first()
    
    def list_all(self) -> List[User]:
        """List all users."""
        return self.db.query(User).options(
            selectinload(User.roles)
        ).all()
    
    def update(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user fields."""
        item = self.get_by_id(user_id)
        if not item:
            return None
        
        for key, value in kwargs.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)
        
        item.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def delete(self, user_id: str) -> bool:
        """Delete a user."""
        item = self.get_by_id(user_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
    
    # ==================== Role Assignment Operations ====================
    
    def assign_role_to_user(self, user_id: str, role_id: str) -> Optional[User]:
        """Assign a role to a user."""
        from auth.modules.role.model import Role
        
        user = self.get_by_id(user_id)
        role = self.db.query(Role).filter(Role.id == role_id).first()
        
        if not user or not role:
            return None
        
        if role not in user.roles:
            user.roles.append(role)
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
        
        return user
    
    def remove_role_from_user(self, user_id: str, role_id: str) -> Optional[User]:
        """Remove a role from a user."""
        from auth.modules.role.model import Role
        
        user = self.get_by_id(user_id)
        role = self.db.query(Role).filter(Role.id == role_id).first()
        
        if not user or not role:
            return None
        
        if role in user.roles:
            user.roles.remove(role)
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
        
        return user
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """Get all permission names for a user."""
        from auth.modules.role.model import Role
        
        user = self.get_by_id(user_id)
        if not user:
            return []
        
        permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(permission.name)
        
        return list(permissions)
