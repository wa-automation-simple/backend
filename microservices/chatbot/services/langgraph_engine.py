"""
LangGraph Engine - Multi-agent orchestration with state management
Handles concurrent chat sessions with optimistic locking
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from config import get_chatbot_settings

settings = get_chatbot_settings()


class LangGraphEngine:
    """
    LangGraph-based multi-agent engine with database state persistence
    Implements optimistic locking for concurrent access
    """
    
    def __init__(self, db: Session, chatbot):
        self.db = db
        self.chatbot = chatbot
        self.settings = settings
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=chatbot.temperature or settings.LLM_TEMPERATURE,
            max_tokens=chatbot.max_tokens or settings.MAX_TOKENS
        )
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow from stored nodes"""
        from models.chatbot_node import ChatbotNode
        
        # Create state graph
        workflow = StateGraph(dict)
        
        # Load nodes from database
        nodes = self.db.query(ChatbotNode).filter(
            ChatbotNode.chatbot_id == self.chatbot.id,
            ChatbotNode.is_active == True
        ).all()
        
        # Add nodes to graph
        for node in nodes:
            if node.node_type == "agent":
                workflow.add_node(node.node_name, self._create_agent_node(node))
            elif node.node_type == "tool":
                workflow.add_node(node.node_name, self._create_tool_node(node))
            elif node.node_type == "conditional":
                workflow.add_node(node.node_name, self._create_conditional_node(node))
            
            # Set entry point
            if node.is_entry_point:
                workflow.set_entry_point(node.node_name)
            
            # Set exit point
            if node.is_exit_point:
                workflow.add_edge(node.node_name, END)
        
        # Add edges from node configuration
        for node in nodes:
            if node.edges:
                for edge in node.edges:
                    if "condition" in edge:
                        # Conditional edge
                        workflow.add_conditional_edges(
                            node.node_name,
                            lambda x: edge["to"],
                            [edge["to"]]
                        )
                    else:
                        # Regular edge
                        workflow.add_edge(node.node_name, edge["to"])
        
        return workflow.compile()
    
    def _create_agent_node(self, node):
        """Create agent node handler"""
        from models.chatbot_agent import ChatbotAgent
        
        async def agent_handler(state: dict):
            # Get agent configuration
            agent = self.db.query(ChatbotAgent).filter(
                ChatbotAgent.chatbot_id == self.chatbot.id,
                ChatbotAgent.name == node.node_config.get("agent_name")
            ).first()
            
            if not agent:
                return state
            
            # Build messages
            messages = []
            if agent.system_prompt:
                messages.append(SystemMessage(content=agent.system_prompt))
            
            # Add conversation history
            for msg in state.get("messages", [])[-self.chatbot.max_context_length:]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
            
            # Get last user message
            last_message = state.get("last_message", "")
            messages.append(HumanMessage(content=last_message))
            
            # Call LLM
            response = await self.llm.ainvoke(messages)
            
            # Update state
            state["messages"].append({
                "role": "assistant",
                "content": response.content,
                "agent": agent.name
            })
            state["current_agent"] = agent.name
            
            return state
        
        return agent_handler
    
    def _create_tool_node(self, node):
        """Create tool node handler"""
        from models.chatbot_tool import ChatbotTool
        
        async def tool_handler(state: dict):
            # Get tool configuration
            tool = self.db.query(ChatbotTool).filter(
                ChatbotTool.chatbot_id == self.chatbot.id,
                ChatbotTool.name == node.node_config.get("tool_name")
            ).first()
            
            if not tool:
                return state
            
            # Execute tool (simplified - implement actual tool logic)
            tool_result = await self._execute_tool(tool, state)
            
            state["messages"].append({
                "role": "tool",
                "content": str(tool_result),
                "tool": tool.name
            })
            
            return state
        
        return tool_handler
    
    def _create_conditional_node(self, node):
        """Create conditional routing node"""
        async def conditional_handler(state: dict):
            # Implement conditional logic based on node configuration
            condition = node.node_config.get("condition", "")
            
            # Simple routing based on keywords
            last_message = state.get("last_message", "").lower()
            
            if "urgent" in last_message or "priority" in last_message:
                return "priority_agent"
            elif "question" in last_message:
                return "qa_agent"
            else:
                return "default_agent"
        
        return conditional_handler
    
    async def _execute_tool(self, tool, state: dict) -> Any:
        """Execute tool based on type"""
        # Implement actual tool execution logic
        # This is a placeholder
        return {"status": "success", "data": None}
    
    async def _acquire_state_lock(self, conversation_id: int, worker_id: str) -> bool:
        """
        Acquire lock on conversation state with optimistic locking
        Returns True if lock acquired, False otherwise
        """
        from models.chatbot_state import ChatbotState
        from sqlalchemy import and_
        
        now = datetime.utcnow()
        
        # Try to acquire lock
        state = self.db.query(ChatbotState).filter(
            ChatbotState.conversation_id == conversation_id
        ).first()
        
        if not state:
            # Create new state
            state = ChatbotState(
                conversation_id=conversation_id,
                chatbot_id=self.chatbot.id,
                state_data={"messages": [], "metadata": {}},
                version=0,
                locked_by=worker_id,
                locked_at=now,
                lock_expires_at=now + timedelta(seconds=self.settings.STATE_LOCK_TIMEOUT)
            )
            self.db.add(state)
            self.db.commit()
            return True
        
        # Check if lock is expired
        if state.locked_at and state.lock_expires_at:
            if now > state.lock_expires_at:
                # Lock expired, acquire it
                state.locked_by = worker_id
                state.locked_at = now
                state.lock_expires_at = now + timedelta(seconds=self.settings.STATE_LOCK_TIMEOUT)
                state.version += 1
                self.db.commit()
                return True
        
        # Check if we already hold the lock
        if state.locked_by == worker_id:
            # Refresh lock
            state.locked_at = now
            state.lock_expires_at = now + timedelta(seconds=self.settings.STATE_LOCK_TIMEOUT)
            self.db.commit()
            return True
        
        # Lock held by another worker
        return False
    
    async def _release_state_lock(self, conversation_id: int, worker_id: str):
        """Release lock on conversation state"""
        from models.chatbot_state import ChatbotState
        
        state = self.db.query(ChatbotState).filter(
            ChatbotState.conversation_id == conversation_id,
            ChatbotState.locked_by == worker_id
        ).first()
        
        if state:
            state.locked_by = None
            state.locked_at = None
            state.lock_expires_at = None
            state.version += 1
            self.db.commit()
    
    async def process_message(
        self,
        conversation_id: int,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user message through LangGraph workflow
        Implements concurrency control with optimistic locking
        """
        import uuid
        import time
        
        worker_id = f"worker_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        # Acquire lock
        lock_acquired = await self._acquire_state_lock(conversation_id, worker_id)
        if not lock_acquired:
            raise Exception("Failed to acquire state lock - conversation is being processed by another request")
        
        try:
            # Load state from database
            from models.chatbot_state import ChatbotState
            
            state_record = self.db.query(ChatbotState).filter(
                ChatbotState.conversation_id == conversation_id
            ).first()
            
            # Initialize state
            state = state_record.state_data if state_record and state_record.state_data else {
                "messages": [],
                "metadata": metadata or {},
                "last_message": message
            }
            
            # Add user message
            state["messages"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            state["last_message"] = message
            
            # Run through LangGraph
            result = await self.graph.ainvoke(state)
            
            # Get assistant response
            assistant_message = None
            for msg in reversed(result.get("messages", [])):
                if msg.get("role") == "assistant":
                    assistant_message = msg
                    break
            
            if not assistant_message:
                assistant_message = {"content": "I'm sorry, I couldn't process your request.", "role": "assistant"}
            
            # Calculate tokens (simplified estimation)
            tokens_used = len(message.split()) + len(assistant_message.get("content", "").split())
            
            # Save updated state
            if state_record:
                state_record.state_data = result
                state_record.message_count = len(result.get("messages", []))
                state_record.total_tokens_used += tokens_used
                state_record.current_node = result.get("current_agent", "unknown")
            else:
                state_record = ChatbotState(
                    conversation_id=conversation_id,
                    chatbot_id=self.chatbot.id,
                    state_data=result,
                    message_count=len(result.get("messages", [])),
                    total_tokens_used=tokens_used
                )
                self.db.add(state_record)
            
            self.db.commit()
            
            return {
                "content": assistant_message.get("content", ""),
                "tokens_used": tokens_used,
                "response_time_ms": (time.time() - start_time) * 1000
            }
        
        finally:
            # Always release lock
            await self._release_state_lock(conversation_id, worker_id)
