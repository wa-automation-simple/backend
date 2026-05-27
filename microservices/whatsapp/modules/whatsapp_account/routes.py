"""API routes for WhatsAppAccount module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from whatsapp.core.database import get_db
from whatsapp.modules.whatsapp_account.schemas import WhatsAppAccountCreate, WhatsAppAccountUpdate, WhatsAppAccountResponse
from whatsapp.modules.whatsapp_account.service import WhatsAppAccountService

router = APIRouter(prefix="/whatsapp_accounts", tags=["WhatsAppAccounts"])


@router.post("", response_model=WhatsAppAccountResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_data: WhatsAppAccountCreate, db: Session = Depends(get_db)):
    """Create a new whatsapp_account."""
    service = WhatsAppAccountService(db)
    return service.create_item(item_data=item_data)


@router.get("", response_model=List[WhatsAppAccountResponse])
def list_items(db: Session = Depends(get_db)):
    """List all items."""
    service = WhatsAppAccountService(db)
    return service.list_items()


@router.get("/{item_id}", response_model=WhatsAppAccountResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get whatsapp_account by ID."""
    service = WhatsAppAccountService(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="WhatsAppAccount not found")
    return item


@router.put("/{item_id}", response_model=WhatsAppAccountResponse)
def update_item(item_id: int, item_data: WhatsAppAccountUpdate, db: Session = Depends(get_db)):
    """Update whatsapp_account."""
    service = WhatsAppAccountService(db)
    item = service.update_item(item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="WhatsAppAccount not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a whatsapp_account."""
    service = WhatsAppAccountService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="WhatsAppAccount not found")
