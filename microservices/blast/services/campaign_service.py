"""Service layer for Blast campaigns."""

from sqlalchemy.orm import Session
from typing import Optional, List, Tuple

from blast.repositories.campaign_repo import BlastCampaignRepository, MediaUploadRepository
from blast.models.blast_campaign import CampaignStatus


class BlastCampaignService:
    """Service for blast campaign operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.campaign_repo = BlastCampaignRepository(db)
        self.media_repo = MediaUploadRepository(db)
    
    def create_campaign(self, user_id: int, name: str, account_id: int, 
                        message_content: str, recipients: List[str],
                        media_url: str = None, media_type: str = None,
                        scheduled_at: str = None) -> dict:
        """Create a new blast campaign."""
        campaign = self.campaign_repo.create(
            user_id=user_id,
            name=name,
            account_id=account_id,
            message_content=message_content,
            recipients=recipients,
            media_url=media_url,
            media_type=media_type,
            scheduled_at=scheduled_at
        )
        
        return {
            "message": "Campaign created successfully",
            "campaign_id": campaign.id,
            "status": campaign.status.value
        }
    
    def get_campaign(self, campaign_id: int):
        return self.campaign_repo.get_by_id(campaign_id)
    
    def list_campaigns(self, user_id: int = None, page: int = 1, page_size: int = 20):
        return self.campaign_repo.list_campaigns(user_id, page, page_size)
    
    def start_campaign(self, campaign_id: int) -> dict:
        """Start a blast campaign."""
        campaign = self.campaign_repo.get_by_id(campaign_id)
        if not campaign:
            raise ValueError("Campaign not found")
        
        from datetime import datetime
        self.campaign_repo.update_status(
            campaign_id, 
            CampaignStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        
        # TODO: Send messages to all recipients
        # This would integrate with WhatsApp service
        
        return {"message": "Campaign started", "campaign_id": campaign_id}
    
    def upload_media(self, user_id: int, filename: str, file_path: str, 
                     file_url: str, file_type: str, file_size: int) -> dict:
        """Register uploaded media."""
        media = self.media_repo.create(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            file_url=file_url,
            file_type=file_type,
            file_size=file_size
        )
        
        return {
            "media_id": media.id,
            "file_url": media.file_url
        }
