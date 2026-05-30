"""Service layer for User business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from passlib.context import CryptContext

from modules.user.model import User
from modules.user.repository import UserRepository
from modules.user.schemas import UserCreate, UserUpdate, GoogleUserCreate


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service layer for User business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)
    
    # ==================== User Operations ====================
    
    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with password hashing."""
        # Check if email already exists
        existing_user = await self.repo.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Hash password
        hashed_password = self._hash_password(user_data.password)
        
        # Create user
        user_dict = user_data.model_dump(exclude={'password'})
        user_dict['hashed_password'] = hashed_password
        
        return await self.repo.create(**user_dict)
    
    async def create_google_user(self, google_data: GoogleUserCreate) -> User:
        """Create a new user from Google OAuth."""
        # Check if Google user already exists
        existing_user = await self.repo.get_by_google_sub(google_data.google_sub)
        if existing_user:
            raise ValueError("Google account already linked")
        
        # Check if email already exists
        existing_user = await self.repo.get_by_email(google_data.google_email)
        if existing_user:
            # Link Google account to existing user
            return await self.repo.update(
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
        
        return await self.repo.create(**user_dict)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = await self.repo.get_by_email(email)
        if not user:
            return None
        
        if not user.hashed_password:
            # User doesn't have a password (Google-only account)
            return None
        
        if not self._verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return await self.repo.get_by_id(user_id)
    
    async def get_user_by_google_sub(self, google_sub: str) -> Optional[User]:
        """Get user by Google subject ID."""
        return await self.repo.get_by_google_sub(google_sub)
    
    async def list_users(self) -> List[User]:
        """List all users."""
        return await self.repo.list_all()
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}
        
        # Handle role assignment separately
        role_ids = update_data.pop('role_ids', None)
        
        user = await self.repo.update(user_id, **update_data)
        
        if user and role_ids is not None:
            # Clear existing roles and assign new ones
            user.roles = []
            await self.db.commit()
            
            for role_id in role_ids:
                await self.repo.assign_role_to_user(user_id, role_id)
            
            # Refresh user with updated roles
            user = await self.repo.get_by_id(user_id)
        
        return user
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        return await self.repo.delete(user_id)
