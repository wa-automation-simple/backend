from enum import Enum
from typing import List, Optional


class RoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    TRIAL = "trial"


class PermissionEnum(str, Enum):
    # User Management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # WhatsApp Accounts
    WA_ACCOUNT_CREATE = "wa_account:create"
    WA_ACCOUNT_READ = "wa_account:read"
    WA_ACCOUNT_UPDATE = "wa_account:update"
    WA_ACCOUNT_DELETE = "wa_account:delete"
    
    # WhatsApp Warming
    WA_WARMUP_START = "wa_warmup:start"
    WA_WARMUP_STOP = "wa_warmup:stop"
    WA_WARMUP_READ = "wa_warmup:read"
    
    # Blast Campaigns
    BLAST_CREATE = "blast:create"
    BLAST_READ = "blast:read"
    BLAST_UPDATE = "blast:update"
    BLAST_DELETE = "blast:delete"
    BLAST_SEND = "blast:send"
    BLAST_WITH_MEDIA = "blast:with_media"
    
    # Auto Reply & AI
    AUTO_REPLY_CREATE = "auto_reply:create"
    AUTO_REPLY_READ = "auto_reply:read"
    AUTO_REPLY_UPDATE = "auto_reply:update"
    AUTO_REPLY_DELETE = "auto_reply:delete"
    AI_USE = "ai:use"
    
    # Token Management
    TOKEN_BUY = "token:buy"
    TOKEN_READ = "token:read"
    TOKEN_TRANSFER = "token:transfer"
    
    # Follow-up
    FOLLOWUP_CREATE = "followup:create"
    FOLLOWUP_READ = "followup:read"
    FOLLOWUP_UPDATE = "followup:update"
    FOLLOWUP_DELETE = "followup:delete"
    
    # Payments
    PAYMENT_CREATE = "payment:create"
    PAYMENT_READ = "payment:read"
    
    # Recovery & Auto Click
    RECOVERY_MANAGE = "recovery:manage"
    AUTO_CLICK_ENABLE = "auto_click:enable"


# Role to Permissions Mapping
ROLE_PERMISSIONS = {
    RoleEnum.SUPER_ADMIN: list(PermissionEnum),
    
    RoleEnum.ADMIN: [
        PermissionEnum.USER_READ,
        PermissionEnum.USER_CREATE,
        PermissionEnum.USER_UPDATE,
        PermissionEnum.WA_ACCOUNT_CREATE,
        PermissionEnum.WA_ACCOUNT_READ,
        PermissionEnum.WA_ACCOUNT_UPDATE,
        PermissionEnum.WA_ACCOUNT_DELETE,
        PermissionEnum.WA_WARMUP_START,
        PermissionEnum.WA_WARMUP_STOP,
        PermissionEnum.WA_WARMUP_READ,
        PermissionEnum.BLAST_CREATE,
        PermissionEnum.BLAST_READ,
        PermissionEnum.BLAST_UPDATE,
        PermissionEnum.BLAST_DELETE,
        PermissionEnum.BLAST_SEND,
        PermissionEnum.BLAST_WITH_MEDIA,
        PermissionEnum.AUTO_REPLY_CREATE,
        PermissionEnum.AUTO_REPLY_READ,
        PermissionEnum.AUTO_REPLY_UPDATE,
        PermissionEnum.AUTO_REPLY_DELETE,
        PermissionEnum.AI_USE,
        PermissionEnum.TOKEN_READ,
        PermissionEnum.FOLLOWUP_CREATE,
        PermissionEnum.FOLLOWUP_READ,
        PermissionEnum.FOLLOWUP_UPDATE,
        PermissionEnum.FOLLOWUP_DELETE,
        PermissionEnum.PAYMENT_READ,
        PermissionEnum.RECOVERY_MANAGE,
        PermissionEnum.AUTO_CLICK_ENABLE,
    ],
    
    RoleEnum.MANAGER: [
        PermissionEnum.USER_READ,
        PermissionEnum.WA_ACCOUNT_CREATE,
        PermissionEnum.WA_ACCOUNT_READ,
        PermissionEnum.WA_ACCOUNT_UPDATE,
        PermissionEnum.WA_WARMUP_START,
        PermissionEnum.WA_WARMUP_READ,
        PermissionEnum.BLAST_CREATE,
        PermissionEnum.BLAST_READ,
        PermissionEnum.BLAST_UPDATE,
        PermissionEnum.BLAST_SEND,
        PermissionEnum.BLAST_WITH_MEDIA,
        PermissionEnum.AUTO_REPLY_CREATE,
        PermissionEnum.AUTO_REPLY_READ,
        PermissionEnum.AUTO_REPLY_UPDATE,
        PermissionEnum.AI_USE,
        PermissionEnum.TOKEN_READ,
        PermissionEnum.FOLLOWUP_CREATE,
        PermissionEnum.FOLLOWUP_READ,
        PermissionEnum.FOLLOWUP_UPDATE,
        PermissionEnum.PAYMENT_READ,
        PermissionEnum.AUTO_CLICK_ENABLE,
    ],
    
    RoleEnum.USER: [
        PermissionEnum.WA_ACCOUNT_CREATE,
        PermissionEnum.WA_ACCOUNT_READ,
        PermissionEnum.WA_ACCOUNT_UPDATE,
        PermissionEnum.WA_WARMUP_START,
        PermissionEnum.WA_WARMUP_READ,
        PermissionEnum.BLAST_CREATE,
        PermissionEnum.BLAST_READ,
        PermissionEnum.BLAST_SEND,
        PermissionEnum.AUTO_REPLY_CREATE,
        PermissionEnum.AUTO_REPLY_READ,
        PermissionEnum.AUTO_REPLY_UPDATE,
        PermissionEnum.AI_USE,
        PermissionEnum.TOKEN_BUY,
        PermissionEnum.TOKEN_READ,
        PermissionEnum.FOLLOWUP_CREATE,
        PermissionEnum.FOLLOWUP_READ,
        PermissionEnum.FOLLOWUP_UPDATE,
        PermissionEnum.PAYMENT_CREATE,
        PermissionEnum.PAYMENT_READ,
        PermissionEnum.AUTO_CLICK_ENABLE,
    ],
    
    RoleEnum.TRIAL: [
        PermissionEnum.WA_ACCOUNT_READ,
        PermissionEnum.WA_WARMUP_READ,
        PermissionEnum.BLAST_READ,
        PermissionEnum.AUTO_REPLY_READ,
        PermissionEnum.TOKEN_READ,
        PermissionEnum.FOLLOWUP_READ,
    ],
}


def get_permissions_for_role(role: RoleEnum) -> List[PermissionEnum]:
    """Get all permissions for a given role"""
    return ROLE_PERMISSIONS.get(role, [])


def has_permission(role: RoleEnum, permission: PermissionEnum) -> bool:
    """Check if a role has a specific permission"""
    permissions = get_permissions_for_role(role)
    return permission in permissions
