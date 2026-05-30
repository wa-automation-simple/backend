"""Repository for ChatbotState database operations."""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from modules.chatbot_state.model import ChatbotState


class ChatbotStateRepository:
    """Repository for ChatbotState model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> ChatbotState:
        """Create a new chatbot_state."""
        item = ChatbotState(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, item_id: int) -> Optional[ChatbotState]:
        """Get chatbot_state by ID."""
        return self.db.query(ChatbotState).filter(ChatbotState.id == item_id).first()
    
    def list_all(self) -> List[ChatbotState]:
        """List all items."""
        return self.db.query(ChatbotState).all()
    
    def update(self, item_id: int, **kwargs) -> Optional[ChatbotState]:
        """Update chatbot_state fields."""
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
        """Delete a chatbot_state."""
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
