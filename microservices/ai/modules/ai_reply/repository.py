"""Repository for AIReply database operations."""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from ai.modules.ai_reply.model import AIReply


class AIReplyRepository:
    """Repository for AIReply model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> AIReply:
        """Create a new ai_reply."""
        item = AIReply(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, item_id: int) -> Optional[AIReply]:
        """Get ai_reply by ID."""
        return self.db.query(AIReply).filter(AIReply.id == item_id).first()
    
    def list_all(self) -> List[AIReply]:
        """List all items."""
        return self.db.query(AIReply).all()
    
    def update(self, item_id: int, **kwargs) -> Optional[AIReply]:
        """Update ai_reply fields."""
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
        """Delete a ai_reply."""
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
