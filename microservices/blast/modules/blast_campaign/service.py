"""Service layer for BlastCampaign business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List

from blast.modules.blast_campaign.model import BlastCampaign
from blast.modules.blast_campaign.repository import BlastCampaignRepository
from blast.modules.blast_campaign.schemas import BlastCampaignCreate, BlastCampaignUpdate


class BlastCampaignService:
    """Service layer for BlastCampaign business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = BlastCampaignRepository(db)
    
    def create_item(self, item_data: BlastCampaignCreate) -> BlastCampaign:
        """Create a new blast_campaign."""
        return self.repo.create(**item_data.model_dump())
    
    def get_item(self, item_id: int) -> Optional[BlastCampaign]:
        """Get blast_campaign by ID."""
        return self.repo.get_by_id(item_id)
    
    def list_items(self) -> List[BlastCampaign]:
        """List all items."""
        return self.repo.list_all()
    
    def update_item(self, item_id: int, item_data: BlastCampaignUpdate) -> Optional[BlastCampaign]:
        """Update blast_campaign."""
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        return self.repo.update(item_id, **update_data)
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a blast_campaign."""
        return self.repo.delete(item_id)
