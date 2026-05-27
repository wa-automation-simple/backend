"""Repository for BlastCampaign database operations."""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from blast.modules.blast_campaign.model import BlastCampaign


class BlastCampaignRepository:
    """Repository for BlastCampaign model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> BlastCampaign:
        """Create a new blast_campaign."""
        item = BlastCampaign(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, item_id: int) -> Optional[BlastCampaign]:
        """Get blast_campaign by ID."""
        return self.db.query(BlastCampaign).filter(BlastCampaign.id == item_id).first()
    
    def list_all(self) -> List[BlastCampaign]:
        """List all items."""
        return self.db.query(BlastCampaign).all()
    
    def update(self, item_id: int, **kwargs) -> Optional[BlastCampaign]:
        """Update blast_campaign fields."""
        item = self.get_by_id(item_id)
        if not item:
            return None
        
        for key, value in kwargs.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)
        
        item.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def delete(self, item_id: int) -> bool:
        """Delete a blast_campaign."""
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
