"""Repository for User database operations."""

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime

from auth.modules.user.model import User, Role, Permission


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
    
    # ==================== Role Operations ====================
    
    def create_role(self, **kwargs) -> Role:
        """Create a new role."""
        permissions = kwargs.pop('permissions', [])
        item = Role(**kwargs)
        item.permissions = permissions
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        return self.db.query(Role).options(
            selectinload(Role.permissions)
        ).filter(Role.id == role_id).first()
    
    def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        return self.db.query(Role).options(
            selectinload(Role.permissions)
        ).filter(Role.name == name).first()
    
    def list_roles(self) -> List[Role]:
        """List all roles."""
        return self.db.query(Role).options(
            selectinload(Role.permissions)
        ).all()
    
    def update_role(self, role_id: str, **kwargs) -> Optional[Role]:
        """Update role fields."""
        item = self.get_role_by_id(role_id)
        if not item:
            return None
        
        permissions = kwargs.pop('permissions', None)
        if permissions is not None:
            item.permissions = permissions
        
        for key, value in kwargs.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)
        
        item.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def delete_role(self, role_id: str) -> bool:
        """Delete a role (only non-system roles)."""
        item = self.get_role_by_id(role_id)
        if not item:
            return False
        
        if item.is_system:
            raise ValueError("Cannot delete system roles")
        
        self.db.delete(item)
        self.db.commit()
        return True
    
    def assign_role_to_user(self, user_id: str, role_id: str) -> Optional[User]:
        """Assign a role to a user."""
        user = self.get_by_id(user_id)
        role = self.get_role_by_id(role_id)
        
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
        user = self.get_by_id(user_id)
        role = self.get_role_by_id(role_id)
        
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
        user = self.get_by_id(user_id)
        if not user:
            return []
        
        permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(permission.name)
        
        return list(permissions)
    
    # ==================== Permission Operations ====================
    
    def create_permission(self, **kwargs) -> Permission:
        """Create a new permission."""
        item = Permission(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_permission_by_id(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID."""
        return self.db.query(Permission).filter(Permission.id == permission_id).first()
    
    def get_permission_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name."""
        return self.db.query(Permission).filter(Permission.name == name).first()
    
    def list_permissions(self) -> List[Permission]:
        """List all permissions."""
        return self.db.query(Permission).all()
    
    def update_permission(self, permission_id: str, **kwargs) -> Optional[Permission]:
        """Update permission fields."""
        item = self.get_permission_by_id(permission_id)
        if not item:
            return None
        
        for key, value in kwargs.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)
        
        item.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def delete_permission(self, permission_id: str) -> bool:
        """Delete a permission."""
        item = self.get_permission_by_id(permission_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
