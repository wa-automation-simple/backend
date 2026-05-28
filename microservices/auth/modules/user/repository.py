"""Repository for User database operations."""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from auth.modules.user.model import User


class UserRepository:
    """Repository for User model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> User:
        """Create a new user."""
        item = User(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, item_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == item_id).first()
    
    def list_all(self) -> List[User]:
        """List all items."""
        return self.db.query(User).all()
    
    def update(self, item_id: int, **kwargs) -> Optional[User]:
        """Update user fields."""
        item = self.get_by_id(item_id)
        if not item:
            return None
        
        for key, value in kwargs.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)
        
        item.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def delete(self, item_id: int) -> bool:
        """Delete a user."""
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
