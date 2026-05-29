"""Repository for Role database operations."""

from sqlalchemy.orm import Session, selectinload
from typing import Optional, List
from datetime import datetime

from auth.modules.role.model import Role


class RoleRepository:
    """Repository for Role model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> Role:
        """Create a new role."""
        permissions = kwargs.pop('permissions', [])
        item = Role(**kwargs)
        item.permissions = permissions
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        return self.db.query(Role).options(
            selectinload(Role.permissions)
        ).filter(Role.id == role_id).first()
    
    def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        return self.db.query(Role).options(
            selectinload(Role.permissions)
        ).filter(Role.name == name).first()
    
    def list_all(self) -> List[Role]:
        """List all roles."""
        return self.db.query(Role).options(
            selectinload(Role.permissions)
        ).all()
    
    def update(self, role_id: str, **kwargs) -> Optional[Role]:
        """Update role fields."""
        item = self.get_by_id(role_id)
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
    
    def delete(self, role_id: str) -> bool:
        """Delete a role (only non-system roles)."""
        item = self.get_by_id(role_id)
        if not item:
            return False
        
        if item.is_system:
            raise ValueError("Cannot delete system roles")
        
        self.db.delete(item)
        self.db.commit()
        return True
