"""Repository for Permission database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime

from modules.permission.model import Permission


class PermissionRepository:
    """Repository for Permission model operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> Permission:
        """Create a new permission."""
        item = Permission(**kwargs)
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def get_by_id(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID."""
        result = await self.db.execute(
            select(Permission).filter(Permission.id == permission_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name."""
        result = await self.db.execute(
            select(Permission).filter(Permission.name == name)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> List[Permission]:
        """List all permissions."""
        result = await self.db.execute(select(Permission))
        return list(result.scalars().all())

    async def update(self, permission_id: str, **kwargs) -> Optional[Permission]:
        """Update permission fields."""
        item = await self.get_by_id(permission_id)
        if not item:
            return None

        for key, value in kwargs.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)

        item.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete(self, permission_id: str) -> bool:
        """Delete a permission."""
        item = await self.get_by_id(permission_id)
        if not item:
            return False

        await self.db.delete(item)
        await self.db.commit()
        return True
