"""Service layer for ChatbotTool business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List

from chatbot.modules.chatbot_tool.model import ChatbotTool
from chatbot.modules.chatbot_tool.repository import ChatbotToolRepository
from chatbot.modules.chatbot_tool.schemas import ChatbotToolCreate, ChatbotToolUpdate


class ChatbotToolService:
    """Service layer for ChatbotTool business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ChatbotToolRepository(db)
    
    def create_item(self, item_data: ChatbotToolCreate) -> ChatbotTool:
        """Create a new chatbot_tool."""
        return self.repo.create(**item_data.model_dump())
    
    def get_item(self, item_id: int) -> Optional[ChatbotTool]:
        """Get chatbot_tool by ID."""
        return self.repo.get_by_id(item_id)
    
    def list_items(self) -> List[ChatbotTool]:
        """List all items."""
        return self.repo.list_all()
    
    def update_item(self, item_id: int, item_data: ChatbotToolUpdate) -> Optional[ChatbotTool]:
        """Update chatbot_tool."""
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        return self.repo.update(item_id, **update_data)
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a chatbot_tool."""
        return self.repo.delete(item_id)
