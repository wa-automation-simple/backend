"""Service layer for Permission business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List

from auth.modules.permission.model import Permission
from auth.modules.permission.repository import PermissionRepository
from auth.modules.permission.schemas import PermissionCreate, PermissionUpdate


class PermissionService:
    """Service layer for Permission business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = PermissionRepository(db)
    
    def create_permission(self, permission_data: PermissionCreate) -> Permission:
        """Create a new permission."""
        # Check if permission name already exists
        existing_perm = self.repo.get_by_name(permission_data.name)
        if existing_perm:
            raise ValueError("Permission name already exists")
        
        return self.repo.create(**permission_data.model_dump())
    
    def get_permission_by_id(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID."""
        return self.repo.get_by_id(permission_id)
    
    def list_permissions(self) -> List[Permission]:
        """List all permissions."""
        return self.repo.list_all()
    
    def update_permission(self, permission_id: str, permission_data: PermissionUpdate) -> Optional[Permission]:
        """Update permission."""
        update_data = {k: v for k, v in permission_data.model_dump().items() if v is not None}
        return self.repo.update(permission_id, **update_data)
    
    def delete_permission(self, permission_id: str) -> bool:
        """Delete a permission."""
        return self.repo.delete(permission_id)
