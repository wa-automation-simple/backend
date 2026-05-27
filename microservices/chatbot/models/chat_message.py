"""
ChatMessage model - Individual messages in conversations
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    
    # Message content
    role = Column(String(50), nullable=False)  # "user", "assistant", "system", "tool"
    content = Column(Text, nullable=False)
    
    # Metadata
    message_type = Column(String(50), default="text")  # "text", "image", "audio", "tool_call"
    tool_calls = Column(JSON, nullable=True)  # If message contains tool calls
    tool_call_id = Column(String(255), nullable=True)  # Reference to tool call if response
    
    # Agent/node info
    agent_name = Column(String(255), nullable=True)  # Which agent generated this
    node_name = Column(String(255), nullable=True)  # Which node processed this
    
    # Token usage
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Status
    is_visible = Column(Boolean, default=True)  # Hide tool messages from user if needed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
