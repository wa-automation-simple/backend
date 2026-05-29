"""API routes for Role module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.database import get_db
from modules.role.schemas import RoleCreate, RoleUpdate, RoleResponse
from modules.role.service import RoleService

router = APIRouter(prefix="/roles", tags=["Roles"])


# ==================== Role Routes ====================

@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(role_data: RoleCreate, db: AsyncSession = Depends(get_db)):
    """Create a new role."""
    service = RoleService(db)
    try:
        return service.create_role(role_data=role_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[RoleResponse])
async def list_roles(db: AsyncSession = Depends(get_db)):
    """List all roles."""
    service = RoleService(db)
    return service.list_roles()


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(role_id: str, db: AsyncSession = Depends(get_db)):
    """Get role by ID."""
    service = RoleService(db)
    role = service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(role_id: str, role_data: RoleUpdate, db: AsyncSession = Depends(get_db)):
    """Update role."""
    service = RoleService(db)
    try:
        role = service.update_role(role_id, role_data)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return role
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a role."""
    service = RoleService(db)
    try:
        success = service.delete_role(role_id)
        if not success:
            raise HTTPException(status_code=404, detail="Role not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
