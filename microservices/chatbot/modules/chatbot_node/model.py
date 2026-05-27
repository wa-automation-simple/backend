"""ChatbotNode module - Auto-generated."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from chatbot.core.database import Base


class ChatbotNode(Base):
    __tablename__ = "chatbot_nodes"

    id = Column(Integer, primary_key=True, index=True)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=False)
    
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

