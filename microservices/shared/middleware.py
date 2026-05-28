"""Middleware for authentication and request logging."""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from shared.security import decode_token, TokenData
from typing import Optional

security = HTTPBearer(auto_error=False)


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
