"""Service layer for ChatbotState business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List

from modules.chatbot_state.model import ChatbotState
from modules.chatbot_state.repository import ChatbotStateRepository
from modules.chatbot_state.schemas import ChatbotStateCreate, ChatbotStateUpdate


class ChatbotStateService:
    """Service layer for ChatbotState business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ChatbotStateRepository(db)
    
    def create_item(self, item_data: ChatbotStateCreate) -> ChatbotState:
        """Create a new chatbot_state."""
        return self.repo.create(**item_data.model_dump())
    
    def get_item(self, item_id: int) -> Optional[ChatbotState]:
        """Get chatbot_state by ID."""
        return self.repo.get_by_id(item_id)
    
    def list_items(self) -> List[ChatbotState]:
        """List all items."""
        return self.repo.list_all()
    
    def update_item(self, item_id: int, item_data: ChatbotStateUpdate) -> Optional[ChatbotState]:
        """Update chatbot_state."""
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        return self.repo.update(item_id, **update_data)
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a chatbot_state."""
        return self.repo.delete(item_id)
