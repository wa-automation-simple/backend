"""User service for business logic operations."""

from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from datetime import datetime

from auth.repositories.user_repo import UserRepository
from auth.models.user import User, UserRole
from auth.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from auth.schemas.serializers import UserCreate, UserUpdate, TokenResponse


class UserService:
    """Service layer for user-related business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)
    
    def register_user(self, user_data: UserCreate) -> User:
        """Register a new user."""
        # Check if username already exists
        existing_user = self.repo.get_by_username(user_data.username)
        if existing_user:
            raise ValueError("Username already taken")
        
        # Check if email already exists
        existing_email = self.repo.get_by_email(user_data.email)
        if existing_email:
            raise ValueError("Email already registered")
        
        # Create user
        user = self.repo.create(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )
        
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[TokenResponse]:
        """Authenticate user and return tokens."""
        user = self.repo.get_by_username(username)
        
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            raise ValueError("User account is deactivated")
        
        # Update last login
        self.repo.update_last_login(user.id)
        
        # Generate tokens
        access_token = create_access_token(
            data={
                "sub": user.id,
                "username": user.username,
                "role": user.role.value,
                "permissions": []  # Will be populated based on role
            }
        )
        
        refresh_token = create_refresh_token(
            data={
                "sub": user.id,
                "username": user.username
            }
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800
        )
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.repo.get_by_id(user_id)
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}
        
        # If updating email, check if it's already taken
        if 'email' in update_data:
            existing = self.repo.get_by_email(update_data['email'])
            if existing and existing.id != user_id:
                raise ValueError("Email already registered")
        
        return self.repo.update(user_id, **update_data)
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        return self.repo.delete(user_id)
    
    def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """List users with pagination."""
        return self.repo.list_users(page, page_size, role, is_active)
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password."""
        user = self.repo.get_by_id(user_id)
        
        if not user or not verify_password(old_password, user.hashed_password):
            raise ValueError("Invalid current password")
        
        from auth.core.security import get_password_hash
        hashed_new_password = get_password_hash(new_password)
        
        self.repo.update(user_id, hashed_password=hashed_new_password)
        return True
    
    def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate a user account."""
        return self.repo.update(user_id, is_active=False)
    
    def activate_user(self, user_id: int) -> Optional[User]:
        """Activate a user account."""
        return self.repo.update(user_id, is_active=True)
    
    def verify_user(self, user_id: int) -> Optional[User]:
        """Verify a user account."""
        return self.repo.verify_user(user_id)
    
    def refresh_tokens(self, refresh_token: str) -> Optional[TokenResponse]:
        """Refresh access token using refresh token."""
        payload = decode_token(refresh_token)
        
        if not payload or payload.get('type') != 'refresh':
            return None
        
        user_id = payload.get('sub')
        user = self.repo.get_by_id(user_id)
        
        if not user or not user.is_active:
            return None
        
        # Generate new tokens
        access_token = create_access_token(
            data={
                "sub": user.id,
                "username": user.username,
                "role": user.role.value
            }
        )
        
        new_refresh_token = create_refresh_token(
            data={
                "sub": user.id,
                "username": user.username
            }
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=1800
        )
