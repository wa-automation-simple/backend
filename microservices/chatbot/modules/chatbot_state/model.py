"""ChatbotState module - Auto-generated."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from datetime import datetime

from core.database import Base


class ChatbotState(Base):
    __tablename__ = "chatbot_states"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    # conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    chatbot_id = Column(UUID(as_uuid=True), ForeignKey("chatbots.id"), nullable=False)
    
    # State data (LangGraph state)
    state_data = Column(JSON, nullable=True)  # Complete state snapshot
    
    # Concurrency control
    version = Column(BigInteger, default=0)  # Optimistic locking version
    locked_by = Column(String(100), nullable=True)  # Session/worker ID holding lock
    locked_at = Column(DateTime, nullable=True)  # When lock was acquired
    lock_expires_at = Column(DateTime, nullable=True)  # Lock expiration time
    
    # State metadata
    current_node = Column(String(255), nullable=True)  # Current node being executed
    message_count = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # conversation = relationship("Conversation", back_populates="states")
    chatbot = relationship("Chatbot")

