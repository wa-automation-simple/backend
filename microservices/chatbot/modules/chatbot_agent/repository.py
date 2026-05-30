"""Repository for ChatbotAgent database operations."""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from modules.chatbot_agent.model import ChatbotAgent


class ChatbotAgentRepository:
    """Repository for ChatbotAgent model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> ChatbotAgent:
        """Create a new chatbot_agent."""
        item = ChatbotAgent(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, item_id: int) -> Optional[ChatbotAgent]:
        """Get chatbot_agent by ID."""
        return self.db.query(ChatbotAgent).filter(ChatbotAgent.id == item_id).first()
    
    def list_all(self) -> List[ChatbotAgent]:
        """List all items."""
        return self.db.query(ChatbotAgent).all()
    
    def update(self, item_id: int, **kwargs) -> Optional[ChatbotAgent]:
        """Update chatbot_agent fields."""
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
        """Delete a chatbot_agent."""
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
