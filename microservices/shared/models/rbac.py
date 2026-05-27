"""
RBAC - Role Based Access Control
Defines roles and permissions for the SaaS platform
"""
from enum import Enum
from typing import List, Dict, Set

class Role(str, Enum):
    SUPER_ADMIN = "super_admin"      # Full access to everything
    ADMIN = "admin"                  # Manage users, billing, settings
    MANAGER = "manager"              # Manage campaigns, blast, followups
    USER = "user"                    # Basic user, can send messages
    TRIAL = "trial"                  # Limited trial user

class Permission(str, Enum):
    # User Management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # WhatsApp Account Management
    WA_ACCOUNT_CREATE = "wa_account:create"
    WA_ACCOUNT_READ = "wa_account:read"
    WA_ACCOUNT_UPDATE = "wa_account:update"
    WA_ACCOUNT_DELETE = "wa_account:delete"
    WA_WARMUP_MANAGE = "wa_warmup:manage"
    WA_MULTI_ACCOUNT = "wa_multi_account"
    
    # Blast Campaigns
    BLAST_CREATE = "blast:create"
    BLAST_READ = "blast:read"
    BLAST_UPDATE = "blast:update"
    BLAST_DELETE = "blast:delete"
    BLAST_SEND = "blast:send"
    BLAST_WITH_MEDIA = "blast:with_media"
    
    # AI Features
    AI_USE = "ai:use"
    AI_CONFIGURE = "ai:configure"
    AI_TOKEN_BUY = "ai_token:buy"
    AI_TOKEN_VIEW = "ai_token:view"
    
    # Auto Reply
    AUTO_REPLY_CREATE = "auto_reply:create"
    AUTO_REPLY_READ = "auto_reply:read"
    AUTO_REPLY_UPDATE = "auto_reply:update"
    AUTO_REPLY_DELETE = "auto_reply:delete"
    
    # Follow-up
    FOLLOWUP_CREATE = "followup:create"
    FOLLOWUP_READ = "followup:read"
    FOLLOWUP_UPDATE = "followup:update"
    FOLLOWUP_DELETE = "followup:delete"
    FOLLOWUP_EXECUTE = "followup:execute"
    
    # Payment & Billing
    PAYMENT_CREATE = "payment:create"
    PAYMENT_READ = "payment:read"
    TOKEN_TOPUP = "token:topup"
    TOKEN_VIEW = "token:view"
    
    # Recovery & Auto-click
    RECOVERY_MANAGE = "recovery:manage"
    AUTO_CLICK_ENABLE = "auto_click:enable"
    
    # Analytics & Reports
    ANALYTICS_VIEW = "analytics:view"
    REPORTS_GENERATE = "reports:generate"

# Role to Permissions mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.SUPER_ADMIN: set(Permission),  # All permissions
    
    Role.ADMIN: {
        Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
        Permission.WA_ACCOUNT_READ, Permission.WA_ACCOUNT_UPDATE,
        Permission.BLAST_READ, Permission.AI_CONFIGURE,
        Permission.PAYMENT_READ, Permission.TOKEN_VIEW,
        Permission.ANALYTICS_VIEW, Permission.REPORTS_GENERATE,
        Permission.FOLLOWUP_READ, Permission.AUTO_REPLY_READ,
    },
    
    Role.MANAGER: {
        Permission.USER_READ,
        Permission.WA_ACCOUNT_READ, Permission.WA_WARMUP_MANAGE,
        Permission.BLAST_CREATE, Permission.BLAST_READ, Permission.BLAST_UPDATE,
        Permission.BLAST_SEND, Permission.BLAST_WITH_MEDIA,
        Permission.AI_USE, Permission.AI_TOKEN_VIEW,
        Permission.AUTO_REPLY_CREATE, Permission.AUTO_REPLY_READ, 
        Permission.AUTO_REPLY_UPDATE,
        Permission.FOLLOWUP_CREATE, Permission.FOLLOWUP_READ,
        Permission.FOLLOWUP_UPDATE, Permission.FOLLOWUP_EXECUTE,
        Permission.TOKEN_VIEW, Permission.ANALYTICS_VIEW,
    },
    
    Role.USER: {
        Permission.USER_READ,
        Permission.WA_ACCOUNT_READ,
        Permission.BLAST_CREATE, Permission.BLAST_READ, Permission.BLAST_SEND,
        Permission.AI_USE,
        Permission.AUTO_REPLY_CREATE, Permission.AUTO_REPLY_READ,
        Permission.FOLLOWUP_CREATE, Permission.FOLLOWUP_READ,
        Permission.TOKEN_VIEW, Permission.TOKEN_TOPUP,
        Permission.RECOVERY_MANAGE,
    },
    
    Role.TRIAL: {
        Permission.USER_READ,
        Permission.WA_ACCOUNT_READ,
        Permission.BLAST_READ,
        Permission.AI_USE,
        Permission.TOKEN_VIEW,
    },
}

def get_role_permissions(role: Role) -> Set[Permission]:
    """Get all permissions for a given role"""
    return ROLE_PERMISSIONS.get(role, set())

def has_permission(role: Role, permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    permissions = get_role_permissions(role)
    return permission in permissions
