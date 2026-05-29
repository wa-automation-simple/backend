"""Role module initialization."""

from auth.modules.role.model import Role, role_permissions
from auth.modules.role.schemas import (
    RoleBase, RoleCreate, RoleUpdate, RoleResponse
)
from auth.modules.role.repository import RoleRepository
from auth.modules.role.service import RoleService
from auth.modules.role.routes import router

__all__ = [
    "Role",
    "role_permissions",
    "RoleBase",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "RoleRepository",
    "RoleService",
    "router",
]
