"""Security utilities: JWT handling, password hashing, and RBAC."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
import os

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """Payload for JWT tokens."""
    user_id: int
    username: str
    role: str
    permissions: list[str] = []


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        username: str = payload.get("username")
        role: str = payload.get("role")
        permissions: list = payload.get("permissions", [])
        
        if user_id is None or username is None:
            return None
        
        return TokenData(
            user_id=user_id,
            username=username,
            role=role,
            permissions=permissions
        )
    except JWTError:
        return None


# RBAC Permissions Matrix
RBAC_PERMISSIONS = {
    "super_admin": ["*"],
    "admin": [
        "user:read", "user:update", "wa_account:read", "wa_account:update",
        "blast:read", "blast:create", "blast:delete", "ai:read", "ai:use",
        "payment:read", "followup:read", "followup:manage"
    ],
    "manager": [
        "user:read", "wa_account:read", "wa_account:create", "wa_account:warmup",
        "blast:read", "blast:create", "ai:use", "followup:read", "followup:create"
    ],
    "user": [
        "wa_account:read", "wa_account:create", "blast:read", "blast:create",
        "ai:use", "followup:read", "followup:create", "token:buy", "token:view"
    ],
    "trial": [
        "wa_account:read", "blast:read", "ai:use_limited"
    ]
}


def check_permission(role: str, required_permission: str) -> bool:
    """Check if a role has the required permission."""
    if role not in RBAC_PERMISSIONS:
        return False
    
    role_permissions = RBAC_PERMISSIONS[role]
    
    # Super admin has all permissions
    if "*" in role_permissions:
        return True
    
    return required_permission in role_permissions


def require_permission(required_permission: str):
    """Dependency injector for FastAPI routes to check permissions."""
    from fastapi import Depends, HTTPException, status
    from .middleware import get_current_user
    
    async def permission_checker(current_user: TokenData = Depends(get_current_user)):
        if not check_permission(current_user.role, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required"
            )
        return current_user
    
    return permission_checker
