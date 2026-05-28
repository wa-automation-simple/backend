"""Service layer for User business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List

from auth.modules.user.model import User
from auth.modules.user.repository import UserRepository
from auth.modules.user.schemas import UserCreate, UserUpdate


class UserService:
    """Service layer for User business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)
    
    def create_item(self, item_data: UserCreate) -> User:
        """Create a new user."""
        return self.repo.create(**item_data.model_dump())
    
    def get_item(self, item_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.repo.get_by_id(item_id)
    
    def list_items(self) -> List[User]:
        """List all items."""
        return self.repo.list_all()
    
    def update_item(self, item_id: int, item_data: UserUpdate) -> Optional[User]:
        """Update user."""
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        return self.repo.update(item_id, **update_data)
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a user."""
        return self.repo.delete(item_id)
