"""Dependencies for WhatsApp service routes."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from whatsapp.core.database import get_db
from whatsapp.services.account_service import WhatsAppAccountService


def get_account_service(db: Session = Depends(get_db)):
    """Get WhatsApp account service instance."""
    return WhatsAppAccountService(db)
