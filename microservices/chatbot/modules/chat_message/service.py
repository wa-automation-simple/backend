"""Service layer for ChatMessage business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List

from modules.chat_message.model import ChatMessage
from modules.chat_message.repository import ChatMessageRepository
from modules.chat_message.schemas import ChatMessageCreate, ChatMessageUpdate


class ChatMessageService:
    """Service layer for ChatMessage business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ChatMessageRepository(db)
    
    def create_item(self, item_data: ChatMessageCreate) -> ChatMessage:
        """Create a new chat_message."""
        return self.repo.create(**item_data.model_dump())
    
    def get_item(self, item_id: int) -> Optional[ChatMessage]:
        """Get chat_message by ID."""
        return self.repo.get_by_id(item_id)
    
    def list_items(self) -> List[ChatMessage]:
        """List all items."""
        return self.repo.list_all()
    
    def update_item(self, item_id: int, item_data: ChatMessageUpdate) -> Optional[ChatMessage]:
        """Update chat_message."""
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        return self.repo.update(item_id, **update_data)
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a chat_message."""
        return self.repo.delete(item_id)
