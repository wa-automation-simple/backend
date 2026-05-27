"""Shared security utilities for all microservices."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """Token payload structure."""
    user_id: Optional[int] = None
    role: Optional[str] = None
    permissions: Optional[list[str]] = None


class RBACPermission:
    """RBAC Permission definitions."""
    
    # User permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # WhatsApp permissions
    WA_ACCOUNT_CREATE = "wa_account:create"
    WA_ACCOUNT_READ = "wa_account:read"
    WA_ACCOUNT_UPDATE = "wa_account:update"
    WA_ACCOUNT_DELETE = "wa_account:delete"
    WA_WARMUP_MANAGE = "wa_warmup:manage"
    WA_SEND_MESSAGE = "wa_send:message"
    
    # Blast permissions
    BLAST_CREATE = "blast:create"
    BLAST_READ = "blast:read"
    BLAST_UPDATE = "blast:update"
    BLAST_DELETE = "blast:delete"
    BLAST_WITH_MEDIA = "blast:with_media"
    
    # AI permissions
    AI_USE = "ai:use"
    AI_TOKEN_READ = "ai_token:read"
    AI_TOKEN_TOPUP = "ai_token:topup"
    AUTO_REPLY_MANAGE = "auto_reply:manage"
    
    # Follow-up permissions
    FOLLOWUP_CREATE = "followup:create"
    FOLLOWUP_READ = "followup:read"
    FOLLOWUP_UPDATE = "followup:update"
    FOLLOWUP_DELETE = "followup:delete"
    
    # Payment permissions
    PAYMENT_CREATE = "payment:create"
    PAYMENT_READ = "payment:read"
    TOKEN_PURCHASE = "token:purchase"
    
    # Recovery permissions
    RECOVERY_MANAGE = "recovery:manage"
    AUTO_CLICK_ENABLE = "auto_click:enable"


# Role-based permissions mapping
ROLE_PERMISSIONS: Dict[str, list[str]] = {
    "super_admin": [
        # Full access to everything
        RBACPermission.USER_CREATE, RBACPermission.USER_READ, RBACPermission.USER_UPDATE, RBACPermission.USER_DELETE,
        RBACPermission.WA_ACCOUNT_CREATE, RBACPermission.WA_ACCOUNT_READ, RBACPermission.WA_ACCOUNT_UPDATE, RBACPermission.WA_ACCOUNT_DELETE,
        RBACPermission.WA_WARMUP_MANAGE, RBACPermission.WA_SEND_MESSAGE,
        RBACPermission.BLAST_CREATE, RBACPermission.BLAST_READ, RBACPermission.BLAST_UPDATE, RBACPermission.BLAST_DELETE, RBACPermission.BLAST_WITH_MEDIA,
        RBACPermission.AI_USE, RBACPermission.AI_TOKEN_READ, RBACPermission.AI_TOKEN_TOPUP, RBACPermission.AUTO_REPLY_MANAGE,
        RBACPermission.FOLLOWUP_CREATE, RBACPermission.FOLLOWUP_READ, RBACPermission.FOLLOWUP_UPDATE, RBACPermission.FOLLOWUP_DELETE,
        RBACPermission.PAYMENT_CREATE, RBACPermission.PAYMENT_READ, RBACPermission.TOKEN_PURCHASE,
        RBACPermission.RECOVERY_MANAGE, RBACPermission.AUTO_CLICK_ENABLE,
    ],
    "admin": [
        # Almost full access, cannot delete users or manage payments
        RBACPermission.USER_CREATE, RBACPermission.USER_READ, RBACPermission.USER_UPDATE,
        RBACPermission.WA_ACCOUNT_CREATE, RBACPermission.WA_ACCOUNT_READ, RBACPermission.WA_ACCOUNT_UPDATE, RBACPermission.WA_ACCOUNT_DELETE,
        RBACPermission.WA_WARMUP_MANAGE, RBACPermission.WA_SEND_MESSAGE,
        RBACPermission.BLAST_CREATE, RBACPermission.BLAST_READ, RBACPermission.BLAST_UPDATE, RBACPermission.BLAST_DELETE, RBACPermission.BLAST_WITH_MEDIA,
        RBACPermission.AI_USE, RBACPermission.AI_TOKEN_READ, RBACPermission.AI_TOKEN_TOPUP, RBACPermission.AUTO_REPLY_MANAGE,
        RBACPermission.FOLLOWUP_CREATE, RBACPermission.FOLLOWUP_READ, RBACPermission.FOLLOWUP_UPDATE, RBACPermission.FOLLOWUP_DELETE,
        RBACPermission.PAYMENT_READ,
        RBACPermission.RECOVERY_MANAGE, RBACPermission.AUTO_CLICK_ENABLE,
    ],
    "manager": [
        # Can manage campaigns and accounts, limited user management
        RBACPermission.USER_READ,
        RBACPermission.WA_ACCOUNT_CREATE, RBACPermission.WA_ACCOUNT_READ, RBACPermission.WA_ACCOUNT_UPDATE,
        RBACPermission.WA_WARMUP_MANAGE, RBACPermission.WA_SEND_MESSAGE,
        RBACPermission.BLAST_CREATE, RBACPermission.BLAST_READ, RBACPermission.BLAST_UPDATE, RBACPermission.BLAST_WITH_MEDIA,
        RBACPermission.AI_USE, RBACPermission.AI_TOKEN_READ, RBACPermission.AUTO_REPLY_MANAGE,
        RBACPermission.FOLLOWUP_CREATE, RBACPermission.FOLLOWUP_READ, RBACPermission.FOLLOWUP_UPDATE,
        RBACPermission.RECOVERY_MANAGE, RBACPermission.AUTO_CLICK_ENABLE,
    ],
    "user": [
        # Basic user access
        RBACPermission.USER_READ, RBACPermission.USER_UPDATE,
        RBACPermission.WA_ACCOUNT_CREATE, RBACPermission.WA_ACCOUNT_READ, RBACPermission.WA_ACCOUNT_UPDATE,
        RBACPermission.WA_WARMUP_MANAGE, RBACPermission.WA_SEND_MESSAGE,
        RBACPermission.BLAST_CREATE, RBACPermission.BLAST_READ, RBACPermission.BLAST_WITH_MEDIA,
        RBACPermission.AI_USE, RBACPermission.AI_TOKEN_READ, RBACPermission.AI_TOKEN_TOPUP, RBACPermission.AUTO_REPLY_MANAGE,
        RBACPermission.FOLLOWUP_CREATE, RBACPermission.FOLLOWUP_READ, RBACPermission.FOLLOWUP_UPDATE,
        RBACPermission.TOKEN_PURCHASE,
        RBACPermission.AUTO_CLICK_ENABLE,
    ],
    "trial": [
        # Limited trial access
        RBACPermission.USER_READ,
        RBACPermission.WA_ACCOUNT_READ,
        RBACPermission.BLAST_READ,
        RBACPermission.AI_TOKEN_READ,
        RBACPermission.FOLLOWUP_READ,
    ],
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        role: str = payload.get("role")
        permissions: list = payload.get("permissions", [])
        
        if user_id is None:
            return None
        
        return TokenData(user_id=user_id, role=role, permissions=permissions)
    except JWTError:
        return None


def get_user_permissions(role: str) -> list[str]:
    """Get permissions for a specific role."""
    return ROLE_PERMISSIONS.get(role, [])


def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission."""
    user_permissions = get_user_permissions(role)
    return permission in user_permissions
