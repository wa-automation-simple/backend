"""
Chatbot model - Main chatbot configuration
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class Chatbot(Base):
    __tablename__ = "chatbots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # LangGraph configuration
    graph_config = Column(JSON, nullable=True)  # Store graph structure
    system_prompt = Column(Text, nullable=True)
    
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
    
    # Relationships
    agents = relationship("ChatbotAgent", back_populates="chatbot", cascade="all, delete-orphan")
    nodes = relationship("ChatbotNode", back_populates="chatbot", cascade="all, delete-orphan")
    tools = relationship("ChatbotTool", back_populates="chatbot", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="chatbot", cascade="all, delete-orphan")
