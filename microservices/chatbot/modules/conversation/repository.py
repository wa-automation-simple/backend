"""Repository for Conversation database operations."""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from modules.conversation.model import Conversation


class ConversationRepository:
    """Repository for Conversation model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> Conversation:
        """Create a new conversation."""
        item = Conversation(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, item_id: int) -> Optional[Conversation]:
        """Get conversation by ID."""
        return self.db.query(Conversation).filter(Conversation.id == item_id).first()
    
    def list_all(self) -> List[Conversation]:
        """List all items."""
        return self.db.query(Conversation).all()
    
    def update(self, item_id: int, **kwargs) -> Optional[Conversation]:
        """Update conversation fields."""
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
        """Delete a conversation."""
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
