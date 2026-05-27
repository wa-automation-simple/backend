"""Repository for Blast campaign operations."""

from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional, List, Tuple
from datetime import datetime
import json

from blast.models.blast_campaign import BlastCampaign, MediaUpload, CampaignStatus


class BlastCampaignRepository:
    """Repository for BlastCampaign operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, name: str, account_id: int, message_content: str, 
               recipients: List[str], media_url: str = None, media_type: str = None, 
               scheduled_at: datetime = None) -> BlastCampaign:
        """Create a new blast campaign."""
        campaign = BlastCampaign(
            user_id=user_id,
            name=name,
            account_id=account_id,
            message_content=message_content,
            recipients=json.dumps(recipients),
            total_recipients=len(recipients),
            media_url=media_url,
            media_type=media_type,
            scheduled_at=scheduled_at,
            status=CampaignStatus.SCHEDULED if scheduled_at else CampaignStatus.DRAFT
        )
        
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign
    
    def get_by_id(self, campaign_id: int) -> Optional[BlastCampaign]:
        return self.db.query(BlastCampaign).filter(BlastCampaign.id == campaign_id).first()
    
    def update_status(self, campaign_id: int, status: CampaignStatus, **kwargs) -> Optional[BlastCampaign]:
        campaign = self.get_by_id(campaign_id)
        if not campaign:
            return None
        
        campaign.status = status
        for key, value in kwargs.items():
            if hasattr(campaign, key):
                setattr(campaign, key, value)
        
        self.db.commit()
        self.db.refresh(campaign)
        return campaign
    
    def list_campaigns(self, user_id: Optional[int] = None, page: int = 1, 
                       page_size: int = 20) -> Tuple[List[BlastCampaign], int]:
        query = select(BlastCampaign)
        if user_id:
            query = query.where(BlastCampaign.user_id == user_id)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar()
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(BlastCampaign.created_at.desc())
        
        campaigns = self.db.execute(query).scalars().all()
        return list(campaigns), total


class MediaUploadRepository:
    """Repository for MediaUpload operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, filename: str, file_path: str, file_url: str, 
               file_type: str, file_size: int) -> MediaUpload:
        media = MediaUpload(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            file_url=file_url,
            file_type=file_type,
            file_size=file_size
        )
        
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)
        return media
    
    def get_by_id(self, media_id: int) -> Optional[MediaUpload]:
        return self.db.query(MediaUpload).filter(MediaUpload.id == media_id).first()
