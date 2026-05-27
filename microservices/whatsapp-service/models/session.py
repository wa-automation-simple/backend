"""WhatsApp Session model for multi-account support."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class WhatsAppSession(Base):
    """WhatsApp session for managing multiple account connections."""
    
    __tablename__ = "whatsapp_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"), nullable=False, index=True)
    
    # Session data
    session_token = Column(String(5000), nullable=False)  # Encrypted session data
    device_id = Column(String(100), nullable=True)
    client_token = Column(String(500), nullable=True)
    server_token = Column(String(500), nullable=True)
    
    # Connection info
    is_connected = Column(Boolean, default=False, nullable=False)
    last_ping = Column(DateTime, nullable=True)
    connection_quality = Column(String(20), default="unknown", nullable=True)  # good, fair, poor
    
    # Recovery info
    recovery_link = Column(String(500), nullable=True)  # Link for auto-click recovery
    is_banned = Column(Boolean, default=False, nullable=False)
    banned_at = Column(DateTime, nullable=True)
    ban_reason = Column(Text, nullable=True)
    
    # Auto-click settings
    auto_click_enabled = Column(Boolean, default=False, nullable=False)
    auto_click_interval = Column(Integer, default=30, nullable=True)  # Seconds between clicks
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<WhatsAppSession(account_id={self.account_id}, connected={self.is_connected})>"
