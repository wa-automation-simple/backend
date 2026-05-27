"""Service layer for ChatbotAgent business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List

from chatbot.modules.chatbot_agent.model import ChatbotAgent
from chatbot.modules.chatbot_agent.repository import ChatbotAgentRepository
from chatbot.modules.chatbot_agent.schemas import ChatbotAgentCreate, ChatbotAgentUpdate


class ChatbotAgentService:
    """Service layer for ChatbotAgent business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ChatbotAgentRepository(db)
    
    def create_item(self, item_data: ChatbotAgentCreate) -> ChatbotAgent:
        """Create a new chatbot_agent."""
        return self.repo.create(**item_data.model_dump())
    
    def get_item(self, item_id: int) -> Optional[ChatbotAgent]:
        """Get chatbot_agent by ID."""
        return self.repo.get_by_id(item_id)
    
    def list_items(self) -> List[ChatbotAgent]:
        """List all items."""
        return self.repo.list_all()
    
    def update_item(self, item_id: int, item_data: ChatbotAgentUpdate) -> Optional[ChatbotAgent]:
        """Update chatbot_agent."""
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        return self.repo.update(item_id, **update_data)
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a chatbot_agent."""
        return self.repo.delete(item_id)
