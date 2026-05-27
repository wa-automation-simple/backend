"""
Follow-up Service Database Models
Dedicated database for leads and follow-ups
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, Array
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class ConversionStatus(enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    NEGOTIATION = "negotiation"
    CONVERTED = "converted"
    LOST = "lost"
    UNSUBSCRIBED = "unsubscribed"


class Lead(Base):
    """Lead/Contact model for follow-up tracking."""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Reference to auth service user
    account_id = Column(Integer, nullable=False)  # WhatsApp account ID
    phone_number = Column(String(20), nullable=False, index=True)
    name = Column(String(200), nullable=True)
    source = Column(String(100), nullable=True)  # Where the lead came from
    conversion_status = Column(SQLEnum(ConversionStatus), default=ConversionStatus.NEW)
    tags = Column(Text, nullable=True)  # JSON array of tags
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_interaction_at = Column(DateTime, nullable=True)
    
    # Relationships
    followups = relationship("FollowUp", back_populates="lead", cascade="all, delete-orphan")
    interaction_logs = relationship("InteractionLog", back_populates="lead", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Lead(id={self.id}, phone='{self.phone_number}', status='{self.conversion_status}')>"


class FollowUpPriority(enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class FollowUpStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class FollowUp(Base):
    """Scheduled follow-up message."""
    __tablename__ = "followups"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    account_id = Column(Integer, nullable=False)  # WhatsApp account to send from
    message = Column(Text, nullable=False)
    scheduled_at = Column(DateTime, nullable=False, index=True)
    status = Column(SQLEnum(FollowUpStatus), default=FollowUpStatus.PENDING)
    priority = Column(SQLEnum(FollowUpPriority), default=FollowUpPriority.NORMAL)
    notes = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    lead = relationship("Lead", back_populates="followups")
    
    def __repr__(self):
        return f"<FollowUp(id={self.id}, scheduled_at={self.scheduled_at}, status='{self.status}')>"


class InteractionType(enum.Enum):
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    CALL_MADE = "call_made"
    EMAIL_SENT = "email_sent"
    NOTE_ADDED = "note_added"
    FOLLOWUP_COMPLETED = "followup_completed"
    STATUS_CHANGED = "status_changed"


class InteractionLog(Base):
    """Interaction history with leads."""
    __tablename__ = "interaction_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    account_id = Column(Integer, nullable=False)
    interaction_type = Column(SQLEnum(InteractionType), nullable=False)
    content = Column(Text, nullable=False)
    metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationship
    lead = relationship("Lead", back_populates="interaction_logs")
    
    def __repr__(self):
        return f"<InteractionLog(id={self.id}, type='{self.interaction_type}', created_at={self.created_at})>"
