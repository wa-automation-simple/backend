"""Service layer for ChatbotNode business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List

from chatbot.modules.chatbot_node.model import ChatbotNode
from chatbot.modules.chatbot_node.repository import ChatbotNodeRepository
from chatbot.modules.chatbot_node.schemas import ChatbotNodeCreate, ChatbotNodeUpdate


class ChatbotNodeService:
    """Service layer for ChatbotNode business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ChatbotNodeRepository(db)
    
    def create_item(self, item_data: ChatbotNodeCreate) -> ChatbotNode:
        """Create a new chatbot_node."""
        return self.repo.create(**item_data.model_dump())
    
    def get_item(self, item_id: int) -> Optional[ChatbotNode]:
        """Get chatbot_node by ID."""
        return self.repo.get_by_id(item_id)
    
    def list_items(self) -> List[ChatbotNode]:
        """List all items."""
        return self.repo.list_all()
    
    def update_item(self, item_id: int, item_data: ChatbotNodeUpdate) -> Optional[ChatbotNode]:
        """Update chatbot_node."""
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        return self.repo.update(item_id, **update_data)
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a chatbot_node."""
        return self.repo.delete(item_id)
