"""Repository for FollowUp database operations."""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from followup.modules.follow_up.model import FollowUp


class FollowUpRepository:
    """Repository for FollowUp model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> FollowUp:
        """Create a new follow_up."""
        item = FollowUp(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, item_id: int) -> Optional[FollowUp]:
        """Get follow_up by ID."""
        return self.db.query(FollowUp).filter(FollowUp.id == item_id).first()
    
    def list_all(self) -> List[FollowUp]:
        """List all items."""
        return self.db.query(FollowUp).all()
    
    def update(self, item_id: int, **kwargs) -> Optional[FollowUp]:
        """Update follow_up fields."""
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
        """Delete a follow_up."""
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
