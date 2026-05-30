"""Service layer for Conversation business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List

from modules.conversation.model import Conversation
from modules.conversation.repository import ConversationRepository
from modules.conversation.schemas import ConversationCreate, ConversationUpdate


class ConversationService:
    """Service layer for Conversation business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ConversationRepository(db)
    
    def create_item(self, item_data: ConversationCreate) -> Conversation:
        """Create a new conversation."""
        return self.repo.create(**item_data.model_dump())
    
    def get_item(self, item_id: int) -> Optional[Conversation]:
        """Get conversation by ID."""
        return self.repo.get_by_id(item_id)
    
    def list_items(self) -> List[Conversation]:
        """List all items."""
        return self.repo.list_all()
    
    def update_item(self, item_id: int, item_data: ConversationUpdate) -> Optional[Conversation]:
        """Update conversation."""
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        return self.repo.update(item_id, **update_data)
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a conversation."""
        return self.repo.delete(item_id)
