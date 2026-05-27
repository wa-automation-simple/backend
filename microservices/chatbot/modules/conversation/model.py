"""Conversation module - Auto-generated."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from chatbot.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Owner of conversation
    
    # Session info
    title = Column(String(255), nullable=True)  # Auto-generated or custom
    session_id = Column(String(255), unique=True, nullable=True)  # For external tracking
    
    # Status
    is_active = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)
    
    # Metadata
    metadata = Column(JSON, nullable=True)  # Custom metadata
    context_window = Column(Integer, default=10)  # Messages to keep in context
    
    # Statistics
    message_count = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    last_message_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chatbot = relationship("Chatbot", back_populates="conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="ChatMessage.created_at")
    states = relationship("ChatbotState", back_populates="conversation", cascade="all, delete-orphan")

