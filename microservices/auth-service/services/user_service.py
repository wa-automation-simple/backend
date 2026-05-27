"""User service for Auth Service - Business Logic Layer."""
from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from datetime import datetime

from ..repositories.user_repo import UserRepository
from ..models.user import User, UserRole
from ..schemas.serializers import UserCreate, UserUpdate
from ...shared.security.rbac import (
    get_password_hash, 
    verify_password,
    create_access_token,
    create_refresh_token,
    get_user_permissions,
    has_permission
)


class UserService:
    """Service layer for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)
    
    def register_user(self, user_data: UserCreate) -> Tuple[User, str]:
        """Register a new user and return user + access token."""
        # Check if email already exists
        existing_user = self.repo.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if username already exists
        existing_username = self.repo.get_by_username(user_data.username)
        if existing_username:
            raise ValueError("Username already taken")
        
        # Hash password
        password_hash = get_password_hash(user_data.password)
        
        # Create user with trial role by default
        user = self.repo.create(
            email=user_data.email,
            username=user_data.username,
            password_hash=password_hash,
            full_name=user_data.full_name,
            role=UserRole.TRIAL
        )
        
        # Generate token
        access_token = self._generate_token(user)
        
        return user, access_token
    
    def authenticate_user(self, email: str, password: str) -> Optional[Tuple[User, str]]:
        """Authenticate user and return user + access token if successful."""
        user = self.repo.get_by_email(email)
        
        if not user:
            return None
        
        if not user.is_active:
            raise ValueError("Account is deactivated")
        
        if not verify_password(password, user.password_hash):
            return None
        
        # Update last login
        self.repo.update_last_login(user.id)
        
        # Generate token
        access_token = self._generate_token(user)
        
        return user, access_token
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.repo.get_by_id(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.repo.get_by_email(email)
    
    def list_users(self, skip: int = 0, limit: int = 100,
                   is_active: Optional[bool] = None,
                   role: Optional[UserRole] = None) -> List[User]:
        """List users with pagination."""
        return self.repo.list_users(skip=skip, limit=limit, is_active=is_active, role=role)
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Check email uniqueness if changing email
        if 'email' in update_data and update_data['email']:
            existing = self.repo.get_by_email(update_data['email'])
            if existing and existing.id != user_id:
                raise ValueError("Email already in use")
        
        return self.repo.update(user_id, **update_data)
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        return self.repo.delete(user_id)
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password."""
        user = self.repo.get_by_id(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        if not verify_password(old_password, user.password_hash):
            raise ValueError("Invalid current password")
        
        # Hash new password
        new_password_hash = get_password_hash(new_password)
        
        self.repo.update(user_id, password_hash=new_password_hash)
        return True
    
    def upgrade_user_role(self, user_id: int, new_role: UserRole) -> Optional[User]:
        """Upgrade user role (admin only)."""
        return self.repo.update(user_id, role=new_role)
    
    def get_user_permissions_list(self, user: User) -> List[str]:
        """Get list of permissions for a user."""
        return get_user_permissions(user.role.value)
    
    def has_user_permission(self, user: User, permission: str) -> bool:
        """Check if user has specific permission."""
        return has_permission(user.role.value, permission)
    
    def _generate_token(self, user: User) -> str:
        """Generate JWT access token for user."""
        permissions = get_user_permissions(user.role.value)
        
        token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role.value,
            "permissions": permissions
        }
        
        return create_access_token(data=token_data)
