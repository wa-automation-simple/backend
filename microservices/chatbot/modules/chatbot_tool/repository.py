"""Repository for ChatbotTool database operations."""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from chatbot.modules.chatbot_tool.model import ChatbotTool


class ChatbotToolRepository:
    """Repository for ChatbotTool model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> ChatbotTool:
        """Create a new chatbot_tool."""
        item = ChatbotTool(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, item_id: int) -> Optional[ChatbotTool]:
        """Get chatbot_tool by ID."""
        return self.db.query(ChatbotTool).filter(ChatbotTool.id == item_id).first()
    
    def list_all(self) -> List[ChatbotTool]:
        """List all items."""
        return self.db.query(ChatbotTool).all()
    
    def update(self, item_id: int, **kwargs) -> Optional[ChatbotTool]:
        """Update chatbot_tool fields."""
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
        """Delete a chatbot_tool."""
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
