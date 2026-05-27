"""LangGraph Integration for Chatbot Service

This module builds dynamic LangGraph workflows based on stored chatbot configurations.
It uses ChatbotAgent, ChatbotNode, ChatbotTool, and ChatbotState models to create
customizable conversation graphs.
"""
from typing import TypedDict, Annotated, List, Optional, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session
import json
import uuid
from datetime import datetime

from chatbot.core.config import settings
from chatbot.modules.chatbot_agent.model import ChatbotAgent
from chatbot.modules.chatbot_node.model import ChatbotNode
from chatbot.modules.chatbot_tool.model import ChatbotTool
from chatbot.modules.chatbot_state.model import ChatbotState
from chatbot.modules.conversation.model import Conversation
from chatbot.modules.chat_message.model import ChatMessage


class AgentState(TypedDict):
    """State for LangGraph workflow - matches ChatbotState model"""
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    current_user_id: Optional[str]
    conversation_id: Optional[int]
    chatbot_id: Optional[int]
    context: Optional[Dict[str, Any]]
    current_node: Optional[str]
    db_session: Optional[Session]
    active_agents: Optional[List[Dict[str, Any]]]
    available_tools: Optional[List[Dict[str, Any]]]


class LangGraphChatbot:
    """Chatbot using LangGraph for stateful conversations with dynamic graph building"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
        self.graph = None
        self.checkpointer = MemorySaver()
    
    def _get_llm(self, model_name: str = "gpt-4o-mini", temperature: float = 0.7):
        """Get LLM instance based on agent configuration"""
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=settings.OPENAI_API_KEY
        )
    
    def _load_chatbot_config(self, chatbot_id: int) -> Dict[str, Any]:
        """Load chatbot configuration from database including agents, nodes, and tools"""
        if not self.db_session:
            raise ValueError("Database session required")
        
        # Load agents
        agents = self.db_session.query(ChatbotAgent).filter(
            ChatbotAgent.chatbot_id == chatbot_id,
            ChatbotAgent.is_active == True
        ).order_by(ChatbotAgent.priority).all()
        
        # Load nodes
        nodes = self.db_session.query(ChatbotNode).filter(
            ChatbotNode.chatbot_id == chatbot_id,
            ChatbotNode.is_active == True
        ).all()
        
        # Load tools
        tools = self.db_session.query(ChatbotTool).filter(
            ChatbotTool.chatbot_id == chatbot_id,
            ChatbotTool.is_active == True
        ).all()
        
        return {
            "agents": agents,
            "nodes": nodes,
            "tools": tools
        }
    
    def _create_agent_node(self, agent: ChatbotAgent):
        """Create a node function for an agent"""
        async def agent_node(state: AgentState) -> AgentState:
            llm = self._get_llm(agent.model_name, agent.temperature)
            
            # Build system prompt
            system_content = agent.system_prompt or "You are a helpful AI assistant."
            messages = [SystemMessage(content=system_content)] + state["messages"]
            
            # Call LLM
            response = await llm.ainvoke(messages)
            
            # Store message in database if session available
            if state.get("db_session") and state.get("conversation_id"):
                self._store_message(
                    db=state["db_session"],
                    conversation_id=state["conversation_id"],
                    role="assistant",
                    content=response.content,
                    agent_name=agent.name,
                    node_name=agent.role
                )
            
            return {
                "messages": [response],
                "current_node": agent.role
            }
        
        return agent_node
    
    def _create_tool_node(self, tool: ChatbotTool):
        """Create a node function for a tool"""
        async def tool_node(state: AgentState) -> AgentState:
            # Execute tool logic based on tool_type
            tool_result = await self._execute_tool(tool, state)
            
            # Store tool result as message
            if state.get("db_session") and state.get("conversation_id"):
                self._store_message(
                    db=state["db_session"],
                    conversation_id=state["conversation_id"],
                    role="tool",
                    content=str(tool_result),
                    tool_call_id=tool.name
                )
            
            return {
                "messages": [ToolMessage(content=str(tool_result), tool_call_id=tool.name)],
                "current_node": f"tool_{tool.name}"
            }
        
        return tool_node
    
    async def _execute_tool(self, tool: ChatbotTool, state: AgentState) -> Any:
        """Execute a tool based on its configuration"""
        tool_config = tool.tool_config or {}
        
        if tool.tool_type == "builtin":
            # Handle builtin tools
            if tool.name == "search":
                # Placeholder for search functionality
                return {"result": "Search results placeholder"}
            elif tool.name == "calculator":
                # Placeholder for calculator
                return {"result": "Calculator result placeholder"}
        
        elif tool.tool_type == "api":
            # Call external API
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    tool_config.get("endpoint", ""),
                    json={"state": state},
                    headers=tool_config.get("headers", {})
                )
                return response.json()
        
        return {"result": f"Tool {tool.name} executed"}
    
    def _store_message(
        self,
        db: Session,
        conversation_id: int,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
        node_name: Optional[str] = None,
        tool_call_id: Optional[str] = None,
        total_tokens: int = 0
    ):
        """Store message in database"""
        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            agent_name=agent_name,
            node_name=node_name,
            tool_call_id=tool_call_id,
            total_tokens=total_tokens
        )
        db.add(message)
        db.commit()
        
        # Update conversation message count
        conversation = db.query(Conversation).get(conversation_id)
        if conversation:
            conversation.message_count += 1
            conversation.last_message_at = datetime.utcnow()
            db.commit()
    
    def _save_state(self, db: Session, conversation_id: int, chatbot_id: int, state: AgentState):
        """Save or update chatbot state in database"""
        existing_state = db.query(ChatbotState).filter(
            ChatbotState.conversation_id == conversation_id
        ).first()
        
        state_data = {
            "messages": [{"type": type(m).__name__, "content": m.content} for m in state.get("messages", [])],
            "current_node": state.get("current_node"),
            "context": state.get("context")
        }
        
        if existing_state:
            existing_state.state_data = state_data
            existing_state.current_node = state.get("current_node")
            existing_state.updated_at = datetime.utcnow()
        else:
            new_state = ChatbotState(
                conversation_id=conversation_id,
                chatbot_id=chatbot_id,
                state_data=state_data,
                current_node=state.get("current_node"),
                message_count=len(state.get("messages", []))
            )
            db.add(new_state)
        
        db.commit()
    
    def _build_graph(self, chatbot_id: int) -> StateGraph:
        """Build LangGraph workflow based on stored configuration"""
        config = self._load_chatbot_config(chatbot_id)
        
        workflow = StateGraph(AgentState)
        
        agents = config["agents"]
        nodes = config["nodes"]
        tools = config["tools"]
        
        # Add agent nodes
        for agent in agents:
            workflow.add_node(agent.role, self._create_agent_node(agent))
        
        # Add tool nodes
        for tool in tools:
            workflow.add_node(f"tool_{tool.name}", self._create_tool_node(tool))
        
        # Add entry point - use first agent or default to first node
        entry_point = None
        if agents:
            entry_point = agents[0].role
        elif nodes:
            entry_node = next((n for n in nodes if n.is_entry_point), nodes[0])
            entry_point = entry_node.node_name
        
        if entry_point:
            workflow.set_entry_point(entry_point)
        
        # Add edges based on node connections
        for node in nodes:
            if node.edges:
                for edge in node.edges:
                    target = edge.get("to")
                    condition = edge.get("condition")
                    
                    if condition:
                        # Conditional edge
                        workflow.add_conditional_edges(
                            node.node_name,
                            lambda x: target,
                            [target]
                        )
                    else:
                        # Regular edge
                        workflow.add_edge(node.node_name, target)
        
        # If no custom nodes, create default flow
        if not nodes:
            if agents:
                # Chain agents in priority order
                for i in range(len(agents) - 1):
                    workflow.add_edge(agents[i].role, agents[i+1].role)
                
                # Last agent goes to END
                workflow.add_edge(agents[-1].role, END)
            else:
                # Default single node flow
                workflow.add_node("default", self._default_node)
                workflow.set_entry_point("default")
                workflow.add_edge("default", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def _default_node(self, state: AgentState) -> AgentState:
        """Default node when no agents/nodes configured"""
        llm = self._get_llm()
        response = await llm.ainvoke(state["messages"])
        return {"messages": [response]}
    
    async def process_message(
        self,
        user_message: str,
        chatbot_id: int,
        conversation_id: Optional[int] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a message through the LangGraph workflow"""
        if not self.db_session:
            raise ValueError("Database session required")
        
        # Build or rebuild graph
        if self.graph is None:
            self.graph = self._build_graph(chatbot_id)
        
        # Create conversation if not provided
        if not conversation_id:
            conversation = Conversation(
                chatbot_id=chatbot_id,
                user_id=user_id or 0,
                title=f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                session_id=str(uuid.uuid4())
            )
            self.db_session.add(conversation)
            self.db_session.commit()
            conversation_id = conversation.id
        
        # Load conversation history
        messages = self.db_session.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at).limit(10).all()
        
        # Convert to LangChain messages
        langchain_messages = []
        for msg in messages:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                langchain_messages.append(SystemMessage(content=msg.content))
            elif msg.role == "tool":
                langchain_messages.append(ToolMessage(content=msg.content, tool_call_id=msg.tool_call_id or ""))
        
        # Add new user message
        langchain_messages.append(HumanMessage(content=user_message))
        
        # Store user message
        self._store_message(
            db=self.db_session,
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )
        
        # Prepare initial state
        initial_state = AgentState(
            messages=langchain_messages,
            current_user_id=user_id,
            conversation_id=conversation_id,
            chatbot_id=chatbot_id,
            context=context or {},
            current_node=None,
            db_session=self.db_session,
            active_agents=None,
            available_tools=None
        )
        
        # Run graph
        config = {"configurable": {"thread_id": str(conversation_id)}}
        result = await self.graph.ainvoke(initial_state, config=config)
        
        # Save state
        self._save_state(self.db_session, conversation_id, chatbot_id, result)
        
        # Get last AI message
        ai_response = ""
        for msg in reversed(result.get("messages", [])):
            if isinstance(msg, AIMessage):
                ai_response = msg.content
                break
        
        return {
            "response": ai_response,
            "conversation_id": conversation_id,
            "messages": result.get("messages", [])
        }
    
    async def chat_stream(
        self,
        user_message: str,
        chatbot_id: int,
        conversation_id: Optional[int] = None,
        user_id: Optional[str] = None
    ):
        """Stream chat response (placeholder for streaming implementation)"""
        result = await self.process_message(
            user_message=user_message,
            chatbot_id=chatbot_id,
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        # Yield response character by character (simplified streaming)
        for char in result["response"]:
            yield char


# Factory function to create chatbot instance with DB session
def get_langgraph_chatbot(db_session: Session) -> LangGraphChatbot:
    """Create LangGraph chatbot instance with database session"""
    return LangGraphChatbot(db_session=db_session)
