"""Service layer for FollowUp business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List

from followup.modules.follow_up.model import FollowUp
from followup.modules.follow_up.repository import FollowUpRepository
from followup.modules.follow_up.schemas import FollowUpCreate, FollowUpUpdate


class FollowUpService:
    """Service layer for FollowUp business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = FollowUpRepository(db)
    
    def create_item(self, item_data: FollowUpCreate) -> FollowUp:
        """Create a new follow_up."""
        return self.repo.create(**item_data.model_dump())
    
    def get_item(self, item_id: int) -> Optional[FollowUp]:
        """Get follow_up by ID."""
        return self.repo.get_by_id(item_id)
    
    def list_items(self) -> List[FollowUp]:
        """List all items."""
        return self.repo.list_all()
    
    def update_item(self, item_id: int, item_data: FollowUpUpdate) -> Optional[FollowUp]:
        """Update follow_up."""
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        return self.repo.update(item_id, **update_data)
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a follow_up."""
        return self.repo.delete(item_id)
