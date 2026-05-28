"""ChatbotAgent module - Auto-generated."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from chatbot.core.database import Base


class ChatbotAgent(Base):
    __tablename__ = "chatbot_agents"

    id = Column(Integer, primary_key=True, index=True)
    # Note: No chatbot_id here - agents are global/reusable, linked via Nodes
    
    # Agent configuration
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)  # e.g., "researcher", "writer", "critic"
    description = Column(Text, nullable=True)
    
    # LLM settings per agent
    model_name = Column(String(100), default="gpt-4o-mini")
    temperature = Column(Integer, default=0.7)
    system_prompt = Column(Text, nullable=True)
    
    # Variable resolution
    variable_pattern = Column(String(500), nullable=True)  # Regex pattern to extract variables from state
    dynamic_script = Column(Text, nullable=True)  # One-line Python script for dynamic prompt/config
    
    # Output schema
    output_schema = Column(JSON, nullable=True)  # Expected output schema for this agent
    
    # Agent behavior
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # For multi-agent orchestration
    agent_config = Column(JSON, nullable=True)  # Additional agent-specific config
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    nodes = relationship("ChatbotNode", back_populates="agent")
    tools = relationship("ChatbotTool", secondary="chatbot_agent_tools", back_populates="agents")

