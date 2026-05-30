"""Repository for Role database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime

from modules.role.model import Role


class RoleRepository:
    """Repository for Role model operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, **kwargs) -> Role:
        """Create a new role."""
        permissions = kwargs.pop('permissions', [])
        item = Role(**kwargs)
        item.permissions = permissions
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item
    
    async def get_by_id(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        result = await self.db.execute(
            select(Role).options(
                selectinload(Role.permissions)
            ).filter(Role.id == role_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        result = await self.db.execute(
            select(Role).options(
                selectinload(Role.permissions)
            ).filter(Role.name == name)
        )
        return result.scalar_one_or_none()
    
    async def list_all(self) -> List[Role]:
        """List all roles."""
        result = await self.db.execute(
            select(Role).options(
                selectinload(Role.permissions)
            )
        )
        return list(result.scalars().all())
    
    async def update(self, role_id: str, **kwargs) -> Optional[Role]:
        """Update role fields."""
        item = await self.get_by_id(role_id)
        if not item:
            return None
        
        permissions = kwargs.pop('permissions', None)
        if permissions is not None:
            item.permissions = permissions
        
        for key, value in kwargs.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)
        
        item.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(item)
        return item
    
    async def delete(self, role_id: str) -> bool:
        """Delete a role (only non-system roles)."""
        item = await self.get_by_id(role_id)
        if not item:
            return False
        
        if item.is_system:
            raise ValueError("Cannot delete system roles")
        
        await self.db.delete(item)
        await self.db.commit()
        return True
