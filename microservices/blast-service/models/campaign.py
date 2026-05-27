"""
Blast Service Database Models
Dedicated database for campaigns and media
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class CampaignStatus(enum.Enum):
    PENDING = "pending"
    SENDING = "sending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BlastCampaign(Base):
    """Blast campaign model."""
    __tablename__ = "blast_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Reference to auth service user
    account_id = Column(Integer, nullable=False)  # WhatsApp account to send from
    name = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.PENDING)
    scheduled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    media_attachments = relationship("CampaignMedia", back_populates="campaign", cascade="all, delete-orphan")
    recipients = relationship("CampaignRecipient", back_populates="campaign", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BlastCampaign(id={self.id}, name='{self.name}', status='{self.status}')>"


class MediaType(enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"


class MediaFile(Base):
    """Media file storage model."""
    __tablename__ = "media_files"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    media_type = Column(SQLEnum(MediaType), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_path = Column(String(500), nullable=False)
    public_url = Column(String(500), nullable=True)
    mime_type = Column(String(100), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<MediaFile(id={self.id}, name='{self.file_name}', type='{self.media_type}')>"


class CampaignMedia(Base):
    """Media attachments for campaigns."""
    __tablename__ = "campaign_media"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("blast_campaigns.id"), nullable=False)
    media_id = Column(Integer, ForeignKey("media_files.id"), nullable=False)
    caption = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    
    # Relationships
    campaign = relationship("BlastCampaign", back_populates="media_attachments")
    media = relationship("MediaFile")
    
    def __repr__(self):
        return f"<CampaignMedia(campaign_id={self.campaign_id}, media_id={self.media_id})>"


class RecipientStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class CampaignRecipient(Base):
    """Campaign recipient tracking."""
    __tablename__ = "campaign_recipients"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("blast_campaigns.id"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    contact_name = Column(String(200), nullable=True)
    status = Column(SQLEnum(RecipientStatus), default=RecipientStatus.PENDING)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationship
    campaign = relationship("BlastCampaign", back_populates="recipients")
    
    def __repr__(self):
        return f"<CampaignRecipient(campaign_id={self.campaign_id}, phone='{self.phone_number}', status='{self.status}')>"
