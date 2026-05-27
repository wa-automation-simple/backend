"""
ChatbotAgent model - Multi-agent system configuration
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class ChatbotAgent(Base):
    __tablename__ = "chatbot_agents"

    id = Column(Integer, primary_key=True, index=True)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=False)
    
    # Agent configuration
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)  # e.g., "researcher", "writer", "critic"
    description = Column(Text, nullable=True)
    
    # LLM settings per agent
    model_name = Column(String(100), default="gpt-4o-mini")
    temperature = Column(Integer, default=0.7)
    system_prompt = Column(Text, nullable=True)
    
    # Agent behavior
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # For multi-agent orchestration
    agent_config = Column(JSON, nullable=True)  # Additional agent-specific config
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chatbot = relationship("Chatbot", back_populates="agents")
