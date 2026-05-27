"""AI Reply Model for Auto-Reply functionality"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ai.core.database import Base


class AIReply(Base):
    __tablename__ = "ai_replies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    whatsapp_account_id = Column(Integer, nullable=False, index=True)
    
    # Trigger configuration
    trigger_type = Column(String(50), default="keyword")  # keyword, always, pattern
    trigger_keywords = Column(JSON, default=list)  # List of keywords to trigger AI
    trigger_pattern = Column(Text, nullable=True)  # Regex pattern
    
    # AI Configuration
    system_prompt = Column(Text, default="You are a helpful customer service assistant.")
    max_tokens = Column(Integer, default=150)
    temperature = Column(Integer, default=0.7)
    
    # Response settings
    enable_ai = Column(Boolean, default=True)
    fallback_message = Column(Text, default="Terima kasih atas pesan Anda. Kami akan segera merespons.")
    
    # Token usage tracking
    tokens_used = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AIReply(id={self.id}, user_id={self.user_id})>"
