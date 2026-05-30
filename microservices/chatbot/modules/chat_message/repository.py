"""Repository for ChatMessage database operations."""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from modules.chat_message.model import ChatMessage


class ChatMessageRepository:
    """Repository for ChatMessage model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> ChatMessage:
        """Create a new chat_message."""
        item = ChatMessage(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, item_id: int) -> Optional[ChatMessage]:
        """Get chat_message by ID."""
        return self.db.query(ChatMessage).filter(ChatMessage.id == item_id).first()
    
    def list_all(self) -> List[ChatMessage]:
        """List all items."""
        return self.db.query(ChatMessage).all()
    
    def update(self, item_id: int, **kwargs) -> Optional[ChatMessage]:
        """Update chat_message fields."""
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
        """Delete a chat_message."""
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
