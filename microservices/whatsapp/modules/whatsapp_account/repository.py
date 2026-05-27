"""Repository for WhatsAppAccount database operations."""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from whatsapp.modules.whatsapp_account.model import WhatsAppAccount


class WhatsAppAccountRepository:
    """Repository for WhatsAppAccount model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> WhatsAppAccount:
        """Create a new whatsapp_account."""
        item = WhatsAppAccount(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_by_id(self, item_id: int) -> Optional[WhatsAppAccount]:
        """Get whatsapp_account by ID."""
        return self.db.query(WhatsAppAccount).filter(WhatsAppAccount.id == item_id).first()
    
    def list_all(self) -> List[WhatsAppAccount]:
        """List all items."""
        return self.db.query(WhatsAppAccount).all()
    
    def update(self, item_id: int, **kwargs) -> Optional[WhatsAppAccount]:
        """Update whatsapp_account fields."""
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
        """Delete a whatsapp_account."""
        item = self.get_by_id(item_id)
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
