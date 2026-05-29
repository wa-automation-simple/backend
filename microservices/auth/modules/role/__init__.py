"""Role module initialization."""

from modules.role.model import Role, role_permissions
from modules.role.schemas import (
    RoleBase, RoleCreate, RoleUpdate, RoleResponse
)
from modules.role.repository import RoleRepository
from modules.role.service import RoleService
from modules.role.routes import router

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
