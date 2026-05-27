"""
RBAC Middleware for request authentication and authorization
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from shared.security import decode_access_token
from shared.config import settings


# RBAC Permissions Matrix
PERMISSIONS = {
    "super_admin": ["*"],  # All permissions
    "admin": [
        "user:read", "user:create", "user:update",
        "wa_account:*", "blast:*", "ai:*",
        "payment:read", "followup:*", "recovery:*"
    ],
    "manager": [
        "user:read",
        "wa_account:read", "wa_account:create", "wa_account:update",
        "blast:read", "blast:create", "blast:send",
        "ai:use", "ai_token:read", "ai_token:purchase",
        "followup:*", "auto_reply:*"
    ],
    "user": [
        "user:read:self",
        "wa_account:read:self", "wa_account:create:self",
        "blast:read:self", "blast:create:self",
        "ai:use:self", "ai_token:read:self", "ai_token:purchase:self",
        "followup:read:self", "auto_reply:manage:self"
    ],
    "trial": [
        "user:read:self",
        "wa_account:read:self",
        "blast:read:self",
        "ai:use:self:limited"
    ]
}


class AuthMiddleware:
    """Authentication and Authorization middleware."""
    
    def __init__(self):
        self.bearer_scheme = HTTPBearer(auto_error=False)
    
    async def __call__(self, request: Request):
        """Validate JWT token and check permissions."""
        # Skip auth for certain paths
        skip_paths = ["/health", "/docs", "/openapi.json", "/register", "/login"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return
        
        # Get token from header
        credentials: HTTPAuthorizationCredentials = await self.bearer_scheme(request)
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Decode token
        payload = decode_access_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Attach user info to request state
        request.state.user_id = payload.get("sub")
        request.state.user_role = payload.get("role", "user")
        request.state.username = payload.get("username")
    
    @staticmethod
    def check_permission(user_role: str, required_permission: str) -> bool:
        """Check if a role has the required permission."""
        if user_role not in PERMISSIONS:
            return False
        
        user_permissions = PERMISSIONS[user_role]
        
        # Super admin has all permissions
        if "*" in user_permissions:
            return True
        
        # Check exact match or wildcard
        for perm in user_permissions:
            if perm == required_permission:
                return True
            # Check wildcard (e.g., "blast:*" matches "blast:create")
            if perm.endswith(":*"):
                prefix = perm[:-2]
                if required_permission.startswith(prefix):
                    return True
        
        return False


auth_middleware = AuthMiddleware()


def require_permission(permission: str):
    """Dependency to require specific permission."""
    async def permission_checker(request: Request):
        user_role = getattr(request.state, "user_role", None)
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        if not AuthMiddleware.check_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )
        
        return True
    
    return permission_checker
