"""ChatbotTool module - Auto-generated."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from chatbot.core.database import Base


class ChatbotTool(Base):
    __tablename__ = "chatbot_tools"

    id = Column(Integer, primary_key=True, index=True)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=False)
    
    # Tool configuration
    name = Column(String(255), nullable=False)  # e.g., "search", "calculator", "database_query"
    tool_type = Column(String(100), nullable=False)  # "builtin", "custom", "api"
    
    # Tool definition
    description = Column(Text, nullable=True)
    tool_schema = Column(JSON, nullable=True)  # JSON Schema for tool parameters
    tool_config = Column(JSON, nullable=True)  # API endpoints, credentials, etc.
    
    # Execution settings
    is_active = Column(Boolean, default=True)
    timeout_seconds = Column(Integer, default=30)
    requires_auth = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chatbot = relationship("Chatbot", back_populates="tools")

