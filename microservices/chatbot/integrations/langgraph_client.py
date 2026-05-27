"""LangGraph Integration for Chatbot Service"""
from typing import TypedDict, Annotated, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from ..core.config import settings


class ChatState(TypedDict):
    """State for chat graph"""
    messages: List[BaseMessage]
    current_user_id: Optional[str]
    conversation_id: Optional[str]
    context: Optional[Dict[str, Any]]


class LangGraphChatbot:
    """Chatbot using LangGraph for stateful conversations"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the chat graph"""
        # Create the graph
        workflow = StateGraph(ChatState)
        
        # Add nodes
        workflow.add_node("process_message", self._process_message)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("store_conversation", self._store_conversation)
        
        # Set entry point
        workflow.set_entry_point("process_message")
        
        # Add edges
        workflow.add_edge("process_message", "generate_response")
        workflow.add_edge("generate_response", "store_conversation")
        workflow.add_edge("store_conversation", END)
        
        return workflow.compile()
    
    async def _process_message(self, state: ChatState) -> ChatState:
        """Process incoming message"""
        messages = state.get("messages", [])
        
        if not messages:
            return state
        
        # Get the last user message
        last_message = messages[-1]
        
        # Add system message if not present
        has_system_message = any(
            isinstance(msg, SystemMessage) for msg in messages
        )
        
        if not has_system_message:
            system_message = SystemMessage(
                content="You are a helpful AI assistant. Be concise and friendly."
            )
            messages.insert(0, system_message)
        
        return {"messages": messages}
    
    async def _generate_response(self, state: ChatState) -> ChatState:
        """Generate response using LLM"""
        if not self.llm_client:
            return {
                "messages": state["messages"] + [
                    AIMessage(content="LLM client not configured")
                ]
            }
        
        messages = state["messages"]
        
        # Convert to format expected by OpenAI
        openai_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                openai_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                openai_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                openai_messages.append({"role": "assistant", "content": msg.content})
        
        # Get response from LLM
        try:
            response = await self.llm_client.chat_completion(
                messages=openai_messages
            )
            
            ai_message = AIMessage(content=response["content"])
            return {"messages": messages + [ai_message]}
        except Exception as e:
            error_message = AIMessage(content=f"Error generating response: {str(e)}")
            return {"messages": messages + [error_message]}
    
    async def _store_conversation(self, state: ChatState) -> ChatState:
        """Store conversation in database (placeholder)"""
        # This would be implemented to store conversation history
        # For now, just return the state
        return state
    
    async def chat(
        self,
        user_message: str,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process a chat message and return response"""
        initial_state = ChatState(
            messages=[HumanMessage(content=user_message)],
            current_user_id=user_id,
            conversation_id=conversation_id,
            context=context or {}
        )
        
        result = await self.graph.ainvoke(initial_state)
        
        # Get the last AI message
        messages = result.get("messages", [])
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                return msg.content
        
        return "No response generated"
    
    async def chat_stream(
        self,
        user_message: str,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ):
        """Stream chat response"""
        # This would implement streaming responses
        # For now, just return the full response
        return await self.chat(user_message, user_id, conversation_id)


# Singleton instance
langgraph_chatbot = LangGraphChatbot()
