"""Shared middleware for all microservices."""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware to validate JWT tokens."""
    
    def __init__(self, app, get_current_user: Callable):
        super().__init__(app)
        self.get_current_user = get_current_user
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Skip auth for login/register endpoints
        if request.url.path.startswith("/api/v1/auth/"):
            return await call_next(request)
        
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid authorization header"}
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            current_user = await self.get_current_user(token)
            if current_user is None:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid or expired token"}
                )
            
            # Attach user to request state
            request.state.current_user = current_user
        except Exception as e:
            logger.error(f"Auth middleware error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication failed"}
            )
        
        return await call_next(request)


class RBACMiddleware(BaseHTTPMiddleware):
    """RBAC middleware to check user permissions."""
    
    def __init__(self, app, required_permission: str):
        super().__init__(app)
        self.required_permission = required_permission
    
    async def dispatch(self, request: Request, call_next):
        # Get current user from request state
        current_user = getattr(request.state, "current_user", None)
        
        if current_user is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"}
            )
        
        # Check if user has required permission
        user_permissions = current_user.get("permissions", [])
        if self.required_permission not in user_permissions:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": f"Permission denied. Required: {self.required_permission}"}
            )
        
        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logging middleware for request/response tracking."""
    
    async def dispatch(self, request: Request, call_next):
        # Log request
        logger.info(f"{request.method} {request.url.path} - {request.client.host}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.info(f"Response status: {response.status_code}")
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )
