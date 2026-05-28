"""Service layer for ChatbotAgent business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List, Dict, Any

from chatbot.modules.chatbot_agent.model import ChatbotAgent
from chatbot.modules.chatbot_agent.schemas import ChatbotAgentCreate, ChatbotAgentUpdate
from chatbot.modules.chatbot_tool.service import VariableResolver, SafeEnvironment


class ChatbotAgentService:
    """Service layer for ChatbotAgent business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.resolver = VariableResolver()
    
    async def create_item(self, item_data: ChatbotAgentCreate) -> ChatbotAgent:
        """Create a new chatbot_agent."""
        agent = ChatbotAgent(**item_data.model_dump())
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        return agent
    
    async def get_item(self, item_id: int) -> Optional[ChatbotAgent]:
        """Get chatbot_agent by ID."""
        result = await self.db.execute(select(ChatbotAgent).where(ChatbotAgent.id == item_id))
        return result.scalar_one_or_none()
    
    async def list_items(self) -> List[ChatbotAgent]:
        """List all items."""
        result = await self.db.execute(select(ChatbotAgent))
        return list(result.scalars().all())
    
    async def update_item(self, item_id: int, item_data: ChatbotAgentUpdate) -> Optional[ChatbotAgent]:
        """Update chatbot_agent."""
        agent = await self.get_item(item_id)
        if not agent:
            return None
        
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        for key, value in update_data.items():
            setattr(agent, key, value)
        
        await self.db.commit()
        await self.db.refresh(agent)
        return agent
    
    async def delete_item(self, item_id: int) -> bool:
        """Delete a chatbot_agent."""
        agent = await self.get_item(item_id)
        if not agent:
            return False
        
        await self.db.delete(agent)
        await self.db.commit()
        return True
    
    async def execute_agent(
        self,
        agent_id: int,
        state: Dict[str, Any],
        messages: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Execute an agent with given state and messages."""
        agent = await self.get_item(agent_id)
        if not agent or not agent.is_active:
            raise ValueError(f"Agent {agent_id} not found or inactive")
        
        # Merge state with input
        context = {**state}
        
        # Resolve dynamic configurations
        if agent.dynamic_script:
            dynamic_result = self.resolver.execute_dynamic_script(agent.dynamic_script, context)
            if dynamic_result:
                context.update(dynamic_result if isinstance(dynamic_result, dict) else {'result': dynamic_result})
        
        if agent.variable_pattern:
            extracted = self.resolver.extract_variables(context, agent.variable_pattern)
            context.update(extracted)
        
        # Resolve system prompt with variables
        system_prompt = agent.system_prompt or ""
        if system_prompt:
            system_prompt = self.resolver.resolve_template(system_prompt, context)
        
        # Prepare messages with resolved variables
        resolved_messages = []
        if messages:
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if isinstance(content, str):
                    content = self.resolver.resolve_template(content, context)
                resolved_messages.append({'role': role, 'content': content})
        
        # Here you would integrate with your LLM provider (OpenAI, etc.)
        # For now, return the resolved prompt and context
        return {
            'agent_id': agent_id,
            'agent_name': agent.name,
            'model_name': agent.model_name,
            'temperature': agent.temperature,
            'system_prompt': system_prompt,
            'messages': resolved_messages,
            'output_schema': agent.output_schema,
            'context': context,
        }
