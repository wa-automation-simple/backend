"""Follow-up Models for Lead Tracking"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from followup.core.database import Base


class FollowUpStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    whatsapp_account_id = Column(Integer, nullable=False, index=True)
    
    # Lead information
    phone_number = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=True)
    tags = Column(Text, nullable=True)  # JSON array of tags
    
    # Source tracking
    source = Column(String(50), default="manual")  # blast, organic, campaign
    campaign_id = Column(Integer, nullable=True)
    
    # Status
    status = Column(SQLEnum(FollowUpStatus), default=FollowUpStatus.PENDING)
    priority = Column(Integer, default=1)  # 1-5 scale
    
    # Notes
    notes = Column(Text, nullable=True)
    last_interaction = Column(DateTime, nullable=True)
    
    # Follow-up schedule
    next_followup_date = Column(DateTime, nullable=True)
    followup_count = Column(Integer, default=0)
    max_followups = Column(Integer, default=5)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Lead(id={self.id}, phone={self.phone_number})>"


class InteractionLog(Base):
    __tablename__ = "interaction_logs"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    whatsapp_account_id = Column(Integer, nullable=False)
    
    # Interaction details
    interaction_type = Column(String(50), nullable=False)  # message_sent, message_received, call, note
    content = Column(Text, nullable=True)
    media_url = Column(String(500), nullable=True)
    
    # Direction
    is_outbound = Column(Boolean, default=True)
    
    # Follow-up reference
    followup_sequence_id = Column(Integer, nullable=True)
    sequence_step = Column(Integer, default=0)
    
    # Response tracking
    response_received = Column(Boolean, default=False)
    response_time_minutes = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<InteractionLog(id={self.id}, lead_id={self.lead_id})>"


class FollowUpSequence(Base):
    __tablename__ = "followup_sequences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Sequence configuration
    total_steps = Column(Integer, default=0)
    interval_days = Column(Integer, default=3)  # Days between follow-ups
    
    # Messages for each step (stored as JSON)
    messages = Column(Text, nullable=True)  # JSON array of message templates
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<FollowUpSequence(id={self.id}, name={self.name})>"
