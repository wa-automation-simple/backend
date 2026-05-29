"""Chatbot module - Auto-generated."""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON, Table, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from chatbot.core.database import Base


# Association table for many-to-many relationship between agents and tools
chatbot_agent_tools = Table(
    'chatbot_agent_tools',
    Base.metadata,
    Column('agent_id', UUID(as_uuid=True), ForeignKey('chatbot_agents.id'), primary_key=True),
    Column('tool_id', UUID(as_uuid=True), ForeignKey('chatbot_tools.id'), primary_key=True)
)


class Chatbot(Base):
    __tablename__ = "chatbots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # LangGraph configuration
    graph_config = Column(JSON, nullable=True)  # Store graph structure
    
    # Settings
    is_active = Column(Boolean, default=True)
    max_context_length = Column(Integer, default=10)
    temperature = Column(Integer, default=0.7)
    max_tokens = Column(Integer, default=2048)
    
    # Static token for /chat endpoint (unique per chatbot)
    static_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - only nodes directly, agents/tools linked via nodes
    nodes = relationship("ChatbotNode", back_populates="chatbot", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="chatbot", cascade="all, delete-orphan")
    tools = relationship("ChatbotTool", back_populates="chatbot", cascade="all, delete-orphan")

