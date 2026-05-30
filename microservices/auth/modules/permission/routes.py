"""API routes for Permission module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.database import get_db
from modules.permission.schemas import PermissionCreate, PermissionUpdate, PermissionResponse
from modules.permission.service import PermissionService

router = APIRouter(prefix="/permissions", tags=["Permissions"])


# ==================== Permission Routes ====================

@router.post("", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(permission_data: PermissionCreate, db: AsyncSession = Depends(get_db)):
    """Create a new permission."""
    service = PermissionService(db)
    try:
        return await service.create_permission(permission_data=permission_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[PermissionResponse])
async def list_permissions(db: AsyncSession = Depends(get_db)):
    """List all permissions."""
    service = PermissionService(db)
    return await service.list_permissions()


@router.get("/{permission_id}", response_model=PermissionResponse)
async def get_permission(permission_id: str, db: AsyncSession = Depends(get_db)):
    """Get permission by ID."""
    service = PermissionService(db)
    permission = await service.get_permission_by_id(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


@router.put("/{permission_id}", response_model=PermissionResponse)
async def update_permission(permission_id: str, permission_data: PermissionUpdate, db: AsyncSession = Depends(get_db)):
    """Update permission."""
    service = PermissionService(db)
    try:
        permission = await service.update_permission(permission_id, permission_data)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        return permission
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(permission_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a permission."""
    service = PermissionService(db)
    success = await service.delete_permission(permission_id)
    if not success:
        raise HTTPException(status_code=404, detail="Permission not found")
