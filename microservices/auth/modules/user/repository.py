"""Repository for User database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime

from modules.user.model import User


class UserRepository:
    """Repository for User model operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== User Operations ====================
    
    async def create(self, **kwargs) -> User:
        """Create a new user."""
        item = User(**kwargs)
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).options(
                selectinload(User.roles)
            ).filter(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).options(
                selectinload(User.roles)
            ).filter(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_google_sub(self, google_sub: str) -> Optional[User]:
        """Get user by Google subject ID."""
        result = await self.db.execute(
            select(User).options(
                selectinload(User.roles)
            ).filter(User.google_sub == google_sub)
        )
        return result.scalar_one_or_none()
    
    async def list_all(self) -> List[User]:
        """List all users."""
        result = await self.db.execute(
            select(User).options(
                selectinload(User.roles)
            )
        )
        return list(result.scalars().all())
    
    async def update(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user fields."""
        item = await self.get_by_id(user_id)
        if not item:
            return None
        
        for key, value in kwargs.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)
        
        item.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(item)
        return item
    
    async def delete(self, user_id: str) -> bool:
        """Delete a user."""
        item = await self.get_by_id(user_id)
        if not item:
            return False
        
        await self.db.delete(item)
        await self.db.commit()
        return True
    
    # ==================== Role Assignment Operations ====================
    
    async def assign_role_to_user(self, user_id: str, role_id: str) -> Optional[User]:
        """Assign a role to a user."""
        from auth.modules.role.model import Role
        
        user = await self.get_by_id(user_id)
        result = await self.db.execute(
            select(Role).filter(Role.id == role_id)
        )
        role = result.scalar_one_or_none()
        
        if not user or not role:
            return None
        
        if role not in user.roles:
            user.roles.append(role)
            user.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(user)
        
        return user
    
    async def remove_role_from_user(self, user_id: str, role_id: str) -> Optional[User]:
        """Remove a role from a user."""
        from auth.modules.role.model import Role
        
        user = await self.get_by_id(user_id)
        result = await self.db.execute(
            select(Role).filter(Role.id == role_id)
        )
        role = result.scalar_one_or_none()
        
        if not user or not role:
            return None
        
        if role in user.roles:
            user.roles.remove(role)
            user.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(user)
        
        return user
    
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get all permission names for a user."""
        from auth.modules.role.model import Role
        
        user = await self.get_by_id(user_id)
        if not user:
            return []
        
        permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(permission.name)
        
        return list(permissions)
