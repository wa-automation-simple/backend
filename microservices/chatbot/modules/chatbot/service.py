"""Service layer for Chatbot business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
from datetime import datetime

from chatbot.modules.chatbot.model import Chatbot
from chatbot.modules.chatbot.repository import ChatbotRepository
from chatbot.modules.chatbot.schemas import ChatbotCreate, ChatbotUpdate


class ChatbotService:
    """Service layer for Chatbot business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ChatbotRepository(db)
    
    def create_item(self, item_data: ChatbotCreate) -> Chatbot:
        """Create a new chatbot with static token."""
        # Generate unique static token for /chat endpoint
        static_token = f"chat_{uuid.uuid4().hex}"
        
        data = item_data.model_dump()
        data['static_token'] = static_token
        
        return self.repo.create(**data)
    
    def get_item(self, item_id: int) -> Optional[Chatbot]:
        """Get chatbot by ID."""
        return self.repo.get_by_id(item_id)
    
    def get_by_static_token(self, static_token: str) -> Optional[Chatbot]:
        """Get chatbot by static token."""
        return self.db.query(Chatbot).filter(Chatbot.static_token == static_token).first()
    
    def list_items(self, user_id: Optional[int] = None) -> List[Chatbot]:
        """List all items, optionally filtered by user_id."""
        query = self.db.query(Chatbot)
        if user_id:
            query = query.filter(Chatbot.user_id == user_id)
        return query.all()
    
    def update_item(self, item_id: int, item_data: ChatbotUpdate) -> Optional[Chatbot]:
        """Update chatbot."""
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        return self.repo.update(item_id, **update_data)
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a chatbot."""
        return self.repo.delete(item_id)
    
    async def process_message(
        self,
        chatbot_id: int,
        user_message: str,
        conversation_id: Optional[int] = None,
        user_id: Optional[str] = None,
        context: Optional[dict] = None
    ) -> dict:
        """Process a message through the LangGraph workflow."""
        # Lazy import to avoid circular dependency
        from chatbot.integrations.langgraph_client import get_langgraph_chatbot
        
        langgraph_bot = get_langgraph_chatbot(self.db)
        result = await langgraph_bot.process_message(
            user_message=user_message,
            chatbot_id=chatbot_id,
            conversation_id=conversation_id,
            user_id=user_id,
            context=context
        )
        return result
    
    def regenerate_static_token(self, chatbot_id: int) -> Optional[str]:
        """Regenerate static token for a chatbot."""
        chatbot = self.get_item(chatbot_id)
        if not chatbot:
            return None
        
        new_token = f"chat_{uuid.uuid4().hex}"
        chatbot.static_token = new_token
        self.db.commit()
        self.db.refresh(chatbot)
        return new_token
