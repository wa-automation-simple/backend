"""Database Seeder for Auth Service - Permissions, Roles, and Users."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

from core.database import Base
from core.config import settings
from modules.permission.model import Permission
from modules.role.model import Role, role_permissions
from modules.user.model import User, user_roles
from passlib.context import CryptContext


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_database():
    """Seed the database with initial permissions, roles, and users."""
    
    # Create async engine using settings
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, autocommit=False, autoflush=False)
    
    async with AsyncSessionLocal() as db:
        try:
            print("🌱 Starting database seeding...")
            
            # ==================== Seed Permissions ====================
            print("\n📋 Seeding permissions...")
            
            permissions_data = [
                # User permissions
                {"name": "user:create", "description": "Create new users", "resource": "user", "action": "create"},
                {"name": "user:read", "description": "View user details", "resource": "user", "action": "read"},
                {"name": "user:update", "description": "Update user information", "resource": "user", "action": "update"},
                {"name": "user:delete", "description": "Delete users", "resource": "user", "action": "delete"},
                {"name": "user:list", "description": "List all users", "resource": "user", "action": "list"},
                
                # Role permissions
                {"name": "role:create", "description": "Create new roles", "resource": "role", "action": "create"},
                {"name": "role:read", "description": "View role details", "resource": "role", "action": "read"},
                {"name": "role:update", "description": "Update role information", "resource": "role", "action": "update"},
                {"name": "role:delete", "description": "Delete roles", "resource": "role", "action": "delete"},
                {"name": "role:list", "description": "List all roles", "resource": "role", "action": "list"},
                
                # Permission permissions
                {"name": "permission:create", "description": "Create new permissions", "resource": "permission", "action": "create"},
                {"name": "permission:read", "description": "View permission details", "resource": "permission", "action": "read"},
                {"name": "permission:update", "description": "Update permission information", "resource": "permission", "action": "update"},
                {"name": "permission:delete", "description": "Delete permissions", "resource": "permission", "action": "delete"},
                {"name": "permission:list", "description": "List all permissions", "resource": "permission", "action": "list"},
                
                # System/Admin permissions
                {"name": "system:manage", "description": "Manage system settings", "resource": "system", "action": "manage"},
                {"name": "audit:read", "description": "View audit logs", "resource": "audit", "action": "read"},
            ]
            
            created_permissions = {}
            for perm_data in permissions_data:
                # Check if permission already exists
                result = await db.execute(
                    Permission.__table__.select().where(Permission.name == perm_data["name"])
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    print(f"  ✓ Permission '{perm_data['name']}' already exists")
                    created_permissions[perm_data["name"]] = existing
                else:
                    permission = Permission(**perm_data)
                    db.add(permission)
                    await db.flush()
                    created_permissions[perm_data["name"]] = permission
                    print(f"  ✓ Created permission '{perm_data['name']}'")
            
            await db.commit()
            print(f"  ✅ Seeded {len(created_permissions)} permissions")
            
            # ==================== Seed Roles ====================
            print("\n👥 Seeding roles...")
            
            # Define roles with their permissions
            roles_data = [
                {
                    "name": "super_admin",
                    "description": "Super Administrator with full access to everything",
                    "is_system": True,
                    "permission_names": list(created_permissions.keys())  # All permissions
                },
                {
                    "name": "admin",
                    "description": "Administrator with management access",
                    "is_system": True,
                    "permission_names": [
                        "user:create", "user:read", "user:update", "user:list",
                        "role:read", "role:list",
                        "permission:read", "permission:list",
                        "audit:read"
                    ]
                },
                {
                    "name": "moderator",
                    "description": "Moderator with limited user management access",
                    "is_system": True,
                    "permission_names": [
                        "user:read", "user:list", "user:update",
                        "role:read", "role:list"
                    ]
                },
                {
                    "name": "user",
                    "description": "Regular user with basic access",
                    "is_system": True,
                    "permission_names": [
                        "user:read"  # Can only read own profile
                    ]
                }
            ]
            
            created_roles = {}
            for role_data in roles_data:
                # Check if role already exists
                result = await db.execute(
                    Role.__table__.select().where(Role.name == role_data["name"])
                )
                existing_role = result.scalar_one_or_none()
                
                if existing_role:
                    print(f"  ✓ Role '{role_data['name']}' already exists")
                    created_roles[role_data["name"]] = existing_role
                else:
                    # Get permission objects
                    permissions = [created_permissions[perm_name] for perm_name in role_data["permission_names"]]
                    
                    role = Role(
                        name=role_data["name"],
                        description=role_data["description"],
                        is_system=role_data["is_system"],
                        permissions=permissions
                    )
                    db.add(role)
                    await db.flush()
                    created_roles[role_data["name"]] = role
                    print(f"  ✓ Created role '{role_data['name']}' with {len(permissions)} permissions")
            
            await db.commit()
            print(f"  ✅ Seeded {len(created_roles)} roles")
            
            # ==================== Seed Users ====================
            print("\n👤 Seeding users...")
            
            users_data = [
                {
                    "username": "superadmin",
                    "name": "Super Administrator",
                    "email": "superadmin@example.com",
                    "password": "SuperAdmin123!",  # Default password - should be changed
                    "is_active": True,
                    "is_verified": True,
                    "role_names": ["super_admin"]
                },
                {
                    "username": "admin",
                    "name": "Administrator",
                    "email": "admin@example.com",
                    "password": "Admin123!",  # Default password - should be changed
                    "is_active": True,
                    "is_verified": True,
                    "role_names": ["admin"]
                },
                {
                    "username": "moderator",
                    "name": "Moderator User",
                    "email": "moderator@example.com",
                    "password": "Moderator123!",  # Default password - should be changed
                    "is_active": True,
                    "is_verified": True,
                    "role_names": ["moderator"]
                },
                {
                    "username": "testuser",
                    "name": "Test User",
                    "email": "user@example.com",
                    "password": "User123!",  # Default password - should be changed
                    "is_active": True,
                    "is_verified": True,
                    "role_names": ["user"]
                }
            ]
            
            created_users = {}
            for user_data in users_data:
                # Check if user already exists
                result = await db.execute(
                    User.__table__.select().where(User.email == user_data["email"])
                )
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    print(f"  ✓ User '{user_data['email']}' already exists")
                    created_users[user_data["email"]] = existing_user
                else:
                    # Hash password
                    hashed_password = pwd_context.hash(user_data["password"])
                    
                    user = User(
                        username=user_data["username"],
                        name=user_data["name"],
                        email=user_data["email"],
                        hashed_password=hashed_password,
                        is_active=user_data["is_active"],
                        is_verified=user_data["is_verified"],
                        google_account_connected=False
                    )
                    db.add(user)
                    await db.flush()
                    
                    # Assign roles
                    for role_name in user_data["role_names"]:
                        role = created_roles.get(role_name)
                        if role:
                            user.roles.append(role)
                    
                    await db.flush()
                    created_users[user_data["email"]] = user
                    print(f"  ✓ Created user '{user_data['email']}' with roles: {', '.join(user_data['role_names'])}")
            
            await db.commit()
            print(f"  ✅ Seeded {len(created_users)} users")
            
            # ==================== Summary ====================
            print("\n" + "="*60)
            print("🎉 Database seeding completed successfully!")
            print("="*60)
            print(f"\n📊 Summary:")
            print(f"   • Permissions: {len(created_permissions)}")
            print(f"   • Roles: {len(created_roles)}")
            print(f"   • Users: {len(created_users)}")
            print(f"\n🔐 Default Super Admin Credentials:")
            print(f"   Email: superadmin@example.com")
            print(f"   Password: SuperAdmin123!")
            print(f"\n⚠️  IMPORTANT: Change default passwords immediately!")
            print("="*60 + "\n")
            
        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error during seeding: {str(e)}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("\n🚀 Auth Service Database Seeder")
    print("="*60)
    asyncio.run(seed_database())
