"""Middleware for authentication and request logging."""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from shared.security import decode_token, TokenData, SECRET_KEY, ALGORITHM
from typing import Optional, Dict, Any
from jose import jwt, JWTError
import os

security = HTTPBearer(auto_error=False)

# Static token header name for chatbot endpoint
STATIC_TOKEN_HEADER = "X-Chatbot-Token"


class AuthMiddleware:
    """Middleware to handle access_token authentication for all requests.
    
    This middleware validates JWT access tokens from the Authorization header.
    For /chatbot/chat endpoint, it validates static_token from X-Chatbot-Token header instead.
    """
    
    def __init__(self, app):
        self.app = app
        # Paths that should be excluded from access_token requirement
        self.excluded_paths = [
            "/health",
            "/",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]
        # Paths that use static token authentication instead of JWT
        self.static_token_paths = [
            "/chatbot/chat",
            "/api/v1/chatbots/chat",
            "/chat-by-token",
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
        
        # Check if path uses static token authentication (e.g., /chatbot/chat)
        if self._is_static_token_path(path):
            # Validate static token from X-Chatbot-Token header
            static_token = request.headers.get(STATIC_TOKEN_HEADER)
            
            if not static_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing static token. Please provide X-Chatbot-Token header.",
                    headers={"WWW-Authenticate": "X-Chatbot-Token"},
                )
            
            # Validate static token against database
            is_valid = await self._validate_static_token(static_token)
            
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid static token",
                    headers={"WWW-Authenticate": "X-Chatbot-Token"},
                )
            
            # Attach chatbot info to request state
            request.state.chatbot_token = static_token
            await self.app(scope, receive, send)
            return
        
        # For all other paths, require JWT access_token
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
        request.state.current_user = user_data
        
        await self.app(scope, receive, send)
    
    def _is_excluded_path(self, path: str) -> bool:
        """Check if the path should be excluded from authentication."""
        for excluded in self.excluded_paths:
            if excluded in path:
                return True
        return False
    
    def _is_static_token_path(self, path: str) -> bool:
        """Check if the path uses static token authentication instead of JWT."""
        for static_path in self.static_token_paths:
            if static_path in path:
                return True
        return False
    
    async def _validate_static_token(self, token: str) -> bool:
        """Validate static token against the database."""
        try:
            from sqlalchemy import select
            from chatbot.core.database import get_db
            from chatbot.modules.chatbot.model import Chatbot
            
            # Get database session
            db_gen = get_db()
            db = next(db_gen)
            
            try:
                # Query chatbot by static token
                stmt = select(Chatbot).where(Chatbot.static_token == token)
                result = db.execute(stmt)
                chatbot = result.scalar_one_or_none()
                
                if chatbot and chatbot.is_active:
                    return True
                return False
            finally:
                db.close()
        except Exception as e:
            print(f"Error validating static token: {e}")
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


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = security
) -> TokenData:
    """Extract and validate JWT token from request headers."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    user_data = decode_token(token)
    
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Store user data in request state for later use
    request.state.current_user = user_data
    return user_data


async def log_requests(request: Request, call_next):
    """Log all incoming requests for debugging and monitoring."""
    import time
    from datetime import datetime
    
    start_time = time.time()
    
    # Get user info if available
    user_id = "anonymous"
    if hasattr(request.state, "current_user"):
        user_id = request.state.current_user.user_id
    
    print(f"[{datetime.now()}] {request.method} {request.url.path} - User: {user_id}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    print(f"[{datetime.now()}] {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
    
    return response
