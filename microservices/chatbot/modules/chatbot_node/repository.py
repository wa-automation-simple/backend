"""Repository for ChatbotNode database operations."""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from modules.chatbot_node.model import ChatbotNode


class ChatbotNodeRepository:
    """Repository for ChatbotNode model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> ChatbotNode:
        """Create a new chatbot_node."""
        item = ChatbotNode(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, item_id: int) -> Optional[ChatbotNode]:
        """Get chatbot_node by ID."""
        return self.db.query(ChatbotNode).filter(ChatbotNode.id == item_id).first()
    
    def list_all(self) -> List[ChatbotNode]:
        """List all items."""
        return self.db.query(ChatbotNode).all()
    
    def update(self, item_id: int, **kwargs) -> Optional[ChatbotNode]:
        """Update chatbot_node fields."""
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
        """Delete a chatbot_node."""
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
