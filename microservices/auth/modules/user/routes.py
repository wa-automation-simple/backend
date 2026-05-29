"""API routes for User module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from auth.core.database import get_db
from auth.modules.user.schemas import (
    UserCreate, UserUpdate, UserResponse,
    RoleCreate, RoleUpdate, RoleResponse,
    PermissionCreate, PermissionUpdate, PermissionResponse,
    GoogleUserCreate, TokenResponse
)
from auth.modules.user.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


# ==================== User Routes ====================

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user."""
    service = UserService(db)
    try:
        return service.create_user(user_data=user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/google", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_google_user(google_data: GoogleUserCreate, db: AsyncSession = Depends(get_db)):
    """Create or link a user via Google OAuth."""
    service = UserService(db)
    try:
        return service.create_google_user(google_data=google_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    """List all users."""
    service = UserService(db)
    return service.list_users()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user by ID."""
    service = UserService(db)
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_data: UserUpdate, db: AsyncSession = Depends(get_db)):
    """Update user."""
    service = UserService(db)
    try:
        user = service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a user."""
    service = UserService(db)
    success = service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/{user_id}/permissions", response_model=List[str])
async def get_user_permissions(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get all permissions for a user."""
    service = UserService(db)
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return service.get_user_permissions(user_id)


# ==================== Role Routes ====================

@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(role_data: RoleCreate, db: AsyncSession = Depends(get_db)):
    """Create a new role."""
    service = UserService(db)
    try:
        return service.create_role(role_data=role_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(db: AsyncSession = Depends(get_db)):
    """List all roles."""
    service = UserService(db)
    return service.list_roles()


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(role_id: str, db: AsyncSession = Depends(get_db)):
    """Get role by ID."""
    service = UserService(db)
    role = service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(role_id: str, role_data: RoleUpdate, db: AsyncSession = Depends(get_db)):
    """Update role."""
    service = UserService(db)
    try:
        role = service.update_role(role_id, role_data)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return role
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a role."""
    service = UserService(db)
    try:
        success = service.delete_role(role_id)
        if not success:
            raise HTTPException(status_code=404, detail="Role not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/{user_id}/roles/{role_id}", response_model=UserResponse)
async def assign_role_to_user(user_id: str, role_id: str, db: AsyncSession = Depends(get_db)):
    """Assign a role to a user."""
    service = UserService(db)
    user = service.assign_role_to_user(user_id, role_id)
    if not user:
        raise HTTPException(status_code=404, detail="User or Role not found")
    return user


@router.delete("/users/{user_id}/roles/{role_id}", response_model=UserResponse)
async def remove_role_from_user(user_id: str, role_id: str, db: AsyncSession = Depends(get_db)):
    """Remove a role from a user."""
    service = UserService(db)
    user = service.remove_role_from_user(user_id, role_id)
    if not user:
        raise HTTPException(status_code=404, detail="User or Role not found")
    return user


# ==================== Permission Routes ====================

@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(permission_data: PermissionCreate, db: AsyncSession = Depends(get_db)):
    """Create a new permission."""
    service = UserService(db)
    try:
        return service.create_permission(permission_data=permission_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(db: AsyncSession = Depends(get_db)):
    """List all permissions."""
    service = UserService(db)
    return service.list_permissions()


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(permission_id: str, db: AsyncSession = Depends(get_db)):
    """Get permission by ID."""
    service = UserService(db)
    permission = service.get_permission_by_id(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(permission_id: str, permission_data: PermissionUpdate, db: AsyncSession = Depends(get_db)):
    """Update permission."""
    service = UserService(db)
    try:
        permission = service.update_permission(permission_id, permission_data)
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        return permission
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(permission_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a permission."""
    service = UserService(db)
    success = service.delete_permission(permission_id)
    if not success:
        raise HTTPException(status_code=404, detail="Permission not found")
