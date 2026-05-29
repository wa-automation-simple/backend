"""Service layer for Role business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List

from modules.role.model import Role
from modules.role.repository import RoleRepository
from modules.role.schemas import RoleCreate, RoleUpdate
from modules.permission.repository import PermissionRepository


class RoleService:
    """Service layer for Role business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = RoleRepository(db)
        self.permission_repo = PermissionRepository(db)
    
    def create_role(self, role_data: RoleCreate) -> Role:
        """Create a new role."""
        # Check if role name already exists
        existing_role = self.repo.get_by_name(role_data.name)
        if existing_role:
            raise ValueError("Role name already exists")
        
        # Get permissions if provided
        permissions = []
        if role_data.permission_ids:
            for perm_id in role_data.permission_ids:
                permission = self.permission_repo.get_by_id(perm_id)
                if permission:
                    permissions.append(permission)
        
        role_dict = role_data.model_dump(exclude={'permission_ids'})
        return self.repo.create(**role_dict, permissions=permissions)
    
    def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        return self.repo.get_by_id(role_id)
    
    def list_roles(self) -> List[Role]:
        """List all roles."""
        return self.repo.list_all()
    
    def update_role(self, role_id: str, role_data: RoleUpdate) -> Optional[Role]:
        """Update role."""
        update_data = {k: v for k, v in role_data.model_dump().items() if v is not None}
        
        # Handle permissions if provided
        permission_ids = update_data.pop('permission_ids', None)
        
        if permission_ids is not None:
            permissions = []
            for perm_id in permission_ids:
                permission = self.permission_repo.get_by_id(perm_id)
                if permission:
                    permissions.append(permission)
            update_data['permissions'] = permissions
        
        return self.repo.update(role_id, **update_data)
    
    def delete_role(self, role_id: str) -> bool:
        """Delete a role."""
        return self.repo.delete(role_id)
