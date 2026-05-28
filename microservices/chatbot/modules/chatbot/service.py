"""Service layer for Chatbot business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
import uuid
from datetime import datetime

from chatbot.modules.chatbot.model import Chatbot
from chatbot.modules.chatbot.schemas import (
    ChatbotCreate, 
    ChatbotUpdate,
)
from chatbot.modules.chatbot_agent.model import ChatbotAgent
from chatbot.modules.chatbot_tool.model import ChatbotTool
from chatbot.modules.chatbot_node.model import ChatbotNode


class ChatbotService:
    """Service layer for Chatbot business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_item(self, item_data: ChatbotCreate, user_id: int) -> Chatbot:
        """Create a new chatbot with static token and all components (agents, tools, nodes)."""
        # Generate unique static token for /chat endpoint
        static_token = f"chat_{uuid.uuid4().hex}"
        
        # Create the chatbot first
        chatbot = Chatbot(
            user_id=user_id,
            name=item_data.name,
            description=item_data.description,
            graph_config=item_data.graph_config,
            is_active=item_data.is_active if hasattr(item_data, 'is_active') else True,
            max_context_length=item_data.max_context_length if hasattr(item_data, 'max_context_length') else 10,
            temperature=item_data.temperature if hasattr(item_data, 'temperature') else 0.7,
            max_tokens=item_data.max_tokens if hasattr(item_data, 'max_tokens') else 2048,
            static_token=static_token
        )
        self.db.add(chatbot)
        await self.db.flush()  # Get the ID without committing
        
        # Create agents
        for agent_data in item_data.agents:
            agent = ChatbotAgent(**agent_data.model_dump())
            self.db.add(agent)
            await self.db.flush()
            
            # Link agent to nodes that reference it
            for node_data in item_data.nodes:
                if node_data.agent_id is None:
                    node_data.agent_id = agent.id
        
        # Create tools
        for tool_data in item_data.tools:
            tool = ChatbotTool(**tool_data.model_dump())
            self.db.add(tool)
            await self.db.flush()
            
            # Link tool to nodes that reference it
            for node_data in item_data.nodes:
                if node_data.tool_id is None and hasattr(node_data, 'tool_name'):
                    if tool_data.name == node_data.tool_name:
                        node_data.tool_id = tool.id
        
        # Create nodes with proper chatbot_id and agent/tool references
        for node_data in item_data.nodes:
            node = ChatbotNode(
                chatbot_id=chatbot.id,
                agent_id=node_data.agent_id,
                tool_id=node_data.tool_id,
                node_name=node_data.node_name,
                node_type=node_data.node_type,
                description=node_data.description,
                node_config=node_data.node_config,
                edges=node_data.edges,
                is_entry_point=node_data.is_entry_point,
                is_exit_point=node_data.is_exit_point,
                is_active=node_data.is_active if hasattr(node_data, 'is_active') else True,
                timeout_seconds=node_data.timeout_seconds if hasattr(node_data, 'timeout_seconds') else 30,
                retry_count=node_data.retry_count if hasattr(node_data, 'retry_count') else 3,
            )
            self.db.add(node)
        
        # Commit all changes
        await self.db.commit()
        await self.db.refresh(chatbot)
        
        return chatbot
    
    async def get_item(self, item_id: int) -> Optional[Chatbot]:
        """Get chatbot by ID with all relationships loaded."""
        result = await self.db.execute(
            select(Chatbot)
            .where(Chatbot.id == item_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_static_token(self, static_token: str) -> Optional[Chatbot]:
        """Get chatbot by static token."""
        result = await self.db.execute(
            select(Chatbot)
            .where(Chatbot.static_token == static_token)
        )
        return result.scalar_one_or_none()
    
    async def list_items(self, user_id: Optional[int] = None) -> List[Chatbot]:
        """List all items, optionally filtered by user_id."""
        query = select(Chatbot)
        if user_id:
            query = query.where(Chatbot.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_item(self, item_id: int, item_data: ChatbotUpdate) -> Optional[Chatbot]:
        """Update chatbot."""
        chatbot = await self.get_item(item_id)
        if not chatbot:
            return None
        
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        for key, value in update_data.items():
            setattr(chatbot, key, value)
        
        await self.db.commit()
        await self.db.refresh(chatbot)
        return chatbot
    
    async def delete_item(self, item_id: int) -> bool:
        """Delete a chatbot."""
        chatbot = await self.get_item(item_id)
        if not chatbot:
            return False
        
        await self.db.delete(chatbot)
        await self.db.commit()
        return True
    
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
    
    async def regenerate_static_token(self, chatbot_id: int) -> Optional[str]:
        """Regenerate static token for a chatbot."""
        chatbot = await self.get_item(chatbot_id)
        if not chatbot:
            return None
        
        new_token = f"chat_{uuid.uuid4().hex}"
        chatbot.static_token = new_token
        await self.db.commit()
        await self.db.refresh(chatbot)
        return new_token
