"""Repository for Permission database operations."""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from modules.permission.model import Permission


class PermissionRepository:
    """Repository for Permission model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> Permission:
        """Create a new permission."""
        item = Permission(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID."""
        return self.db.query(Permission).filter(Permission.id == permission_id).first()
    
    def get_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name."""
        return self.db.query(Permission).filter(Permission.name == name).first()
    
    def list_all(self) -> List[Permission]:
        """List all permissions."""
        return self.db.query(Permission).all()
    
    def update(self, permission_id: str, **kwargs) -> Optional[Permission]:
        """Update permission fields."""
        item = self.get_by_id(permission_id)
        if not item:
            return None
        
        for key, value in kwargs.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)
        
        item.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def delete(self, permission_id: str) -> bool:
        """Delete a permission."""
        item = self.get_by_id(permission_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
