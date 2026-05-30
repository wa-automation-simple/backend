"""Service layer for Permission business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from modules.permission.model import Permission
from modules.permission.repository import PermissionRepository
from modules.permission.schemas import PermissionCreate, PermissionUpdate


class PermissionService:
    """Service layer for Permission business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PermissionRepository(db)

    async def create_permission(self, permission_data: PermissionCreate) -> Permission:
        """Create a new permission."""
        # Check if permission name already exists
        existing_perm = await self.repo.get_by_name(permission_data.name)
        if existing_perm:
            raise ValueError("Permission name already exists")

        return await self.repo.create(**permission_data.model_dump())

    async def get_permission_by_id(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID."""
        return await self.repo.get_by_id(permission_id)

    async def list_permissions(self) -> List[Permission]:
        """List all permissions."""
        return await self.repo.list_all()

    async def update_permission(
        self, permission_id: str, permission_data: PermissionUpdate
    ) -> Optional[Permission]:
        """Update permission."""
        update_data = {
            k: v for k, v in permission_data.model_dump().items() if v is not None
        }
        return await self.repo.update(permission_id, **update_data)

    async def delete_permission(self, permission_id: str) -> bool:
        """Delete a permission."""
        return await self.repo.delete(permission_id)
