"""Service layer for WhatsAppAccount business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List

from whatsapp.modules.whatsapp_account.model import WhatsAppAccount
from whatsapp.modules.whatsapp_account.repository import WhatsAppAccountRepository
from whatsapp.modules.whatsapp_account.schemas import WhatsAppAccountCreate, WhatsAppAccountUpdate


class WhatsAppAccountService:
    """Service layer for WhatsAppAccount business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = WhatsAppAccountRepository(db)
    
    def create_item(self, item_data: WhatsAppAccountCreate) -> WhatsAppAccount:
        """Create a new whatsapp_account."""
        return self.repo.create(**item_data.model_dump())
    
    def get_item(self, item_id: int) -> Optional[WhatsAppAccount]:
        """Get whatsapp_account by ID."""
        return self.repo.get_by_id(item_id)
    
    def list_items(self) -> List[WhatsAppAccount]:
        """List all items."""
        return self.repo.list_all()
    
    def update_item(self, item_id: int, item_data: WhatsAppAccountUpdate) -> Optional[WhatsAppAccount]:
        """Update whatsapp_account."""
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        return self.repo.update(item_id, **update_data)
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a whatsapp_account."""
        return self.repo.delete(item_id)
