"""Service layer for AIReply business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List

from ai.modules.ai_reply.model import AIReply
from ai.modules.ai_reply.repository import AIReplyRepository
from ai.modules.ai_reply.schemas import AIReplyCreate, AIReplyUpdate


class AIReplyService:
    """Service layer for AIReply business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = AIReplyRepository(db)
    
    def create_item(self, item_data: AIReplyCreate) -> AIReply:
        """Create a new ai_reply."""
        return self.repo.create(**item_data.model_dump())
    
    def get_item(self, item_id: int) -> Optional[AIReply]:
        """Get ai_reply by ID."""
        return self.repo.get_by_id(item_id)
    
    def list_items(self) -> List[AIReply]:
        """List all items."""
        return self.repo.list_all()
    
    def update_item(self, item_id: int, item_data: AIReplyUpdate) -> Optional[AIReply]:
        """Update ai_reply."""
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        return self.repo.update(item_id, **update_data)
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a ai_reply."""
        return self.repo.delete(item_id)
