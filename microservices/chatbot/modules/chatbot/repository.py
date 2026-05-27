"""Repository for Chatbot database operations."""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from chatbot.modules.chatbot.model import Chatbot


class ChatbotRepository:
    """Repository for Chatbot model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> Chatbot:
        """Create a new chatbot."""
        item = Chatbot(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, item_id: int) -> Optional[Chatbot]:
        """Get chatbot by ID."""
        return self.db.query(Chatbot).filter(Chatbot.id == item_id).first()
    
    def list_all(self) -> List[Chatbot]:
        """List all items."""
        return self.db.query(Chatbot).all()
    
    def update(self, item_id: int, **kwargs) -> Optional[Chatbot]:
        """Update chatbot fields."""
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
        """Delete a chatbot."""
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
