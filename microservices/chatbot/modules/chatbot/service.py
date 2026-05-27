"""Service layer for Chatbot business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List

from chatbot.modules.chatbot.model import Chatbot
from chatbot.modules.chatbot.repository import ChatbotRepository
from chatbot.modules.chatbot.schemas import ChatbotCreate, ChatbotUpdate


class ChatbotService:
    """Service layer for Chatbot business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ChatbotRepository(db)
    
    def create_item(self, item_data: ChatbotCreate) -> Chatbot:
        """Create a new chatbot."""
        return self.repo.create(**item_data.model_dump())
    
    def get_item(self, item_id: int) -> Optional[Chatbot]:
        """Get chatbot by ID."""
        return self.repo.get_by_id(item_id)
    
    def list_items(self) -> List[Chatbot]:
        """List all items."""
        return self.repo.list_all()
    
    def update_item(self, item_id: int, item_data: ChatbotUpdate) -> Optional[Chatbot]:
        """Update chatbot."""
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        return self.repo.update(item_id, **update_data)
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a chatbot."""
        return self.repo.delete(item_id)
