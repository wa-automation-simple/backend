"""API routes for BlastCampaign module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from blast.core.database import get_db
from blast.modules.blast_campaign.schemas import BlastCampaignCreate, BlastCampaignUpdate, BlastCampaignResponse
from blast.modules.blast_campaign.service import BlastCampaignService

router = APIRouter(prefix="/blast_campaigns", tags=["BlastCampaigns"])


@router.post("", response_model=BlastCampaignResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_data: BlastCampaignCreate, db: Session = Depends(get_db)):
    """Create a new blast_campaign."""
    service = BlastCampaignService(db)
    return service.create_item(item_data=item_data)


@router.get("", response_model=List[BlastCampaignResponse])
def list_items(db: Session = Depends(get_db)):
    """List all items."""
    service = BlastCampaignService(db)
    return service.list_items()


@router.get("/{item_id}", response_model=BlastCampaignResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get blast_campaign by ID."""
    service = BlastCampaignService(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="BlastCampaign not found")
    return item


@router.put("/{item_id}", response_model=BlastCampaignResponse)
def update_item(item_id: int, item_data: BlastCampaignUpdate, db: Session = Depends(get_db)):
    """Update blast_campaign."""
    service = BlastCampaignService(db)
    item = service.update_item(item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="BlastCampaign not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a blast_campaign."""
    service = BlastCampaignService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="BlastCampaign not found")
