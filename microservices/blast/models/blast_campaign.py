"""Blast Campaign and Media models."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from blast.core.database import Base


class CampaignStatus(str, enum.Enum):
    """Campaign status."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"


class BlastCampaign(Base):
    """Blast campaign for bulk messaging."""
    
    __tablename__ = "blast_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    account_id = Column(Integer, nullable=False)  # WhatsApp account ID to send from
    message_content = Column(Text, nullable=False)
    media_url = Column(String(500), nullable=True)
    media_type = Column(String(20), nullable=True)  # image, video, etc.
    recipients = Column(Text, nullable=False)  # JSON array of phone numbers
    total_recipients = Column(Integer, nullable=False)
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    sent_count = Column(Integer, default=0, nullable=False)
    delivered_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<BlastCampaign(id={self.id}, name='{self.name}', status='{self.status}')>"


class MediaUpload(Base):
    """Media files uploaded for blast campaigns."""
    
    __tablename__ = "media_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # image/jpeg, video/mp4, etc.
    file_size = Column(Integer, nullable=False)  # in bytes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<MediaUpload(id={self.id}, filename='{self.filename}')>"
