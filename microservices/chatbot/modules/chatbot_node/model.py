"""ChatbotNode module - Auto-generated."""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from chatbot.core.database import Base


class ChatbotNode(Base):
    __tablename__ = "chatbot_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    chatbot_id = Column(UUID(as_uuid=True), ForeignKey("chatbots.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("chatbot_agents.id"), nullable=True)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("chatbot_tools.id"), nullable=True)
    
    # Node configuration
    node_name = Column(String(255), nullable=False)  # e.g., "researcher_node", "writer_node"
    node_type = Column(String(100), nullable=False)  # "agent", "tool", "conditional", "entry", "exit"
    
    # Node logic
    description = Column(Text, nullable=True)
    node_config = Column(JSON, nullable=True)  # Node-specific configuration
    
    # Graph connections
    edges = Column(JSON, nullable=True)  # Store edge connections: [{"to": "node_name", "condition": "..."}]
    is_entry_point = Column(Boolean, default=False)
    is_exit_point = Column(Boolean, default=False)
    
    # Execution settings
    is_active = Column(Boolean, default=True)
    timeout_seconds = Column(Integer, default=30)
    retry_count = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chatbot = relationship("Chatbot", back_populates="nodes")
    agent = relationship("ChatbotAgent", back_populates="nodes")
    tool = relationship("ChatbotTool", back_populates="nodes")

