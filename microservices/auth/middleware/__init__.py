"""Authentication middleware for FastAPI services."""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from typing import Optional, Dict, Any

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey_change_in_production")
ALGORITHM = "HS256"

security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """Middleware to handle access_token authentication for all requests.
    
    This middleware validates JWT access tokens from the Authorization header.
    It excludes the /chatbot/chat endpoint which uses static token authentication.
    """
    
    def __init__(self, app):
        self.app = app
        # Paths that should be excluded from access_token requirement
        self.excluded_paths = [
            "/chatbot/chat",
            "/api/v1/chatbots/chat",
            "/chat-by-token",
            "/health",
            "/",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope)
        path = request.url.path
        
        # Check if path should be excluded from authentication
        if self._is_excluded_path(path):
            await self.app(scope, receive, send)
            return
        
        # Get token from Authorization header
        credentials: Optional[HTTPAuthorizationCredentials] = await security(request)
        
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        
        # Validate the token
        user_data = self._validate_token(token)
        
        if user_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Attach user data to request state for use in route handlers
        request.state.user = user_data
        
        await self.app(scope, receive, send)
    
    def _is_excluded_path(self, path: str) -> bool:
        """Check if the path should be excluded from authentication."""
        for excluded in self.excluded_paths:
            if excluded in path:
                return True
        return False
    
    def _validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT access token and return user data."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            user_id = payload.get("sub")
            username = payload.get("username")
            role = payload.get("role", "user")
            permissions = payload.get("permissions", [])
            
            if user_id is None or username is None:
                return None
            
            # Check token type is 'access'
            token_type = payload.get("type")
            if token_type != "access":
                return None
            
            return {
                "user_id": user_id,
                "username": username,
                "role": role,
                "permissions": permissions,
            }
        except JWTError:
            return None


def get_current_user(request: Request) -> Dict[str, Any]:
    """Dependency to get current user from request state.
    
    Usage in routes:
        @router.get("/me")
        def get_me(current_user: dict = Depends(get_current_user)):
            return current_user
    """
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


def require_permission(required_permission: str):
    """Dependency to check if user has required permission.
    
    Usage in routes:
        @router.delete("/item/{id}")
        def delete_item(id: int, current_user: dict = Depends(require_permission("item:delete"))):
            ...
    """
    from fastapi import Depends
    
    async def permission_checker(current_user: dict = Depends(get_current_user)):
        # Super admin has all permissions
        if current_user.get("role") == "super_admin":
            return current_user
        
        user_permissions = current_user.get("permissions", [])
        
        # Check for wildcard permission
        if "*" in user_permissions:
            return current_user
        
        if required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required",
            )
        
        return current_user
    
    return permission_checker
