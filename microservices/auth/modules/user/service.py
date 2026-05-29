"""Service layer for User business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List
from passlib.context import CryptContext

from auth.modules.user.model import User, Role, Permission
from auth.modules.user.repository import UserRepository
from auth.modules.user.schemas import (
    UserCreate, UserUpdate, GoogleUserCreate,
    RoleCreate, RoleUpdate,
    PermissionCreate, PermissionUpdate
)


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service layer for User business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)
    
    # ==================== User Operations ====================
    
    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with password hashing."""
        # Check if email already exists
        existing_user = self.repo.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Hash password
        hashed_password = self._hash_password(user_data.password)
        
        # Create user
        user_dict = user_data.model_dump(exclude={'password'})
        user_dict['hashed_password'] = hashed_password
        
        return self.repo.create(**user_dict)
    
    def create_google_user(self, google_data: GoogleUserCreate) -> User:
        """Create a new user from Google OAuth."""
        # Check if Google user already exists
        existing_user = self.repo.get_by_google_sub(google_data.google_sub)
        if existing_user:
            raise ValueError("Google account already linked")
        
        # Check if email already exists
        existing_user = self.repo.get_by_email(google_data.google_email)
        if existing_user:
            # Link Google account to existing user
            return self.repo.update(
                existing_user.id,
                google_account_connected=True,
                google_sub=google_data.google_sub,
                google_email=google_data.google_email,
                google_name=google_data.google_name,
                google_picture=google_data.google_picture
            )
        
        # Create new user
        user_dict = {
            'username': google_data.google_name or google_data.google_email.split('@')[0],
            'email': google_data.google_email,
            'hashed_password': None,  # No password for Google users
            'google_account_connected': True,
            'google_sub': google_data.google_sub,
            'google_email': google_data.google_email,
            'google_name': google_data.google_name,
            'google_picture': google_data.google_picture,
            'is_verified': True,  # Google emails are verified
        }
        
        return self.repo.create(**user_dict)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = self.repo.get_by_email(email)
        if not user:
            return None
        
        if not user.hashed_password:
            # User doesn't have a password (Google-only account)
            return None
        
        if not self._verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.repo.get_by_id(user_id)
    
    def get_user_by_google_sub(self, google_sub: str) -> Optional[User]:
        """Get user by Google subject ID."""
        return self.repo.get_by_google_sub(google_sub)
    
    def list_users(self) -> List[User]:
        """List all users."""
        return self.repo.list_all()
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}
        
        # Handle role assignment separately
        role_ids = update_data.pop('role_ids', None)
        
        user = self.repo.update(user_id, **update_data)
        
        if user and role_ids is not None:
            # Clear existing roles and assign new ones
            user.roles = []
            self.db.commit()
            
            for role_id in role_ids:
                self.repo.assign_role_to_user(user_id, role_id)
            
            # Refresh user with updated roles
            user = self.repo.get_by_id(user_id)
        
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        return self.repo.delete(user_id)
    
    # ==================== Role Operations ====================
    
    def create_role(self, role_data: RoleCreate) -> Role:
        """Create a new role."""
        # Check if role name already exists
        existing_role = self.repo.get_role_by_name(role_data.name)
        if existing_role:
            raise ValueError("Role name already exists")
        
        # Get permissions if provided
        permissions = []
        if role_data.permission_ids:
            for perm_id in role_data.permission_ids:
                permission = self.repo.get_permission_by_id(perm_id)
                if permission:
                    permissions.append(permission)
        
        role_dict = role_data.model_dump(exclude={'permission_ids'})
        return self.repo.create_role(**role_dict, permissions=permissions)
    
    def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        return self.repo.get_role_by_id(role_id)
    
    def list_roles(self) -> List[Role]:
        """List all roles."""
        return self.repo.list_roles()
    
    def update_role(self, role_id: str, role_data: RoleUpdate) -> Optional[Role]:
        """Update role."""
        update_data = {k: v for k, v in role_data.model_dump().items() if v is not None}
        
        # Handle permissions if provided
        permission_ids = update_data.pop('permission_ids', None)
        
        if permission_ids is not None:
            permissions = []
            for perm_id in permission_ids:
                permission = self.repo.get_permission_by_id(perm_id)
                if permission:
                    permissions.append(permission)
            update_data['permissions'] = permissions
        
        return self.repo.update_role(role_id, **update_data)
    
    def delete_role(self, role_id: str) -> bool:
        """Delete a role."""
        return self.repo.delete_role(role_id)
    
    def assign_role_to_user(self, user_id: str, role_id: str) -> Optional[User]:
        """Assign a role to a user."""
        return self.repo.assign_role_to_user(user_id, role_id)
    
    def remove_role_from_user(self, user_id: str, role_id: str) -> Optional[User]:
        """Remove a role from a user."""
        return self.repo.remove_role_from_user(user_id, role_id)
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """Get all permissions for a user."""
        return self.repo.get_user_permissions(user_id)
    
    def has_permission(self, user_id: str, permission_name: str) -> bool:
        """Check if user has a specific permission."""
        permissions = self.get_user_permissions(user_id)
        return permission_name in permissions
    
    # ==================== Permission Operations ====================
    
    def create_permission(self, permission_data: PermissionCreate) -> Permission:
        """Create a new permission."""
        # Check if permission name already exists
        existing_perm = self.repo.get_permission_by_name(permission_data.name)
        if existing_perm:
            raise ValueError("Permission name already exists")
        
        return self.repo.create_permission(**permission_data.model_dump())
    
    def get_permission_by_id(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID."""
        return self.repo.get_permission_by_id(permission_id)
    
    def list_permissions(self) -> List[Permission]:
        """List all permissions."""
        return self.repo.list_permissions()
    
    def update_permission(self, permission_id: str, permission_data: PermissionUpdate) -> Optional[Permission]:
        """Update permission."""
        update_data = {k: v for k, v in permission_data.model_dump().items() if v is not None}
        return self.repo.update_permission(permission_id, **update_data)
    
    def delete_permission(self, permission_id: str) -> bool:
        """Delete a permission."""
        return self.repo.delete_permission(permission_id)
