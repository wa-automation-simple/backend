"""
Blast Service - Bulk messaging with media support
"""
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from shared.utils.database import get_db, engine, Base
from shared.schemas.serializers import (
    BlastCampaignCreate, BlastCampaignResponse, BlastCampaignUpdate,
    MediaUploadResponse, MessageResponse
)
from shared.models.tables import User, BlastCampaign, TokenBalance
from shared.models.rbac import RequirePermission

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Blast Service",
    description="WhatsApp Blast Campaign Management with Media Support",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "blast-service"}


@app.post("/campaigns", response_model=BlastCampaignResponse)
async def create_blast_campaign(
    campaign_data: BlastCampaignCreate,
    current_user: User = Depends(RequirePermission("blast:create")),
    db: Session = Depends(get_db)
):
    """Create new blast campaign"""
    # Check token balance
    token_balance = db.query(TokenBalance).filter(
        TokenBalance.user_id == current_user.id
    ).first()
    
    if not token_balance or token_balance.balance < len(campaign_data.recipient_list):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient token balance. Please top up."
        )
    
    campaign = BlastCampaign(
        user_id=current_user.id,
        name=campaign_data.name,
        message=campaign_data.message,
        media_url=campaign_data.media_url,
        media_type=campaign_data.media_type,
        recipient_list=campaign_data.recipient_list,
        scheduled_at=campaign_data.scheduled_at,
        status="scheduled" if campaign_data.scheduled_at else "draft"
    )
    
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    return campaign


@app.get("/campaigns", response_model=List[BlastCampaignResponse])
async def list_blast_campaigns(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(RequirePermission("blast:read")),
    db: Session = Depends(get_db)
):
    """List all blast campaigns for current user"""
    campaigns = db.query(BlastCampaign).filter(
        BlastCampaign.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return campaigns


@app.get("/campaigns/{campaign_id}", response_model=BlastCampaignResponse)
async def get_blast_campaign(
    campaign_id: int,
    current_user: User = Depends(RequirePermission("blast:read")),
    db: Session = Depends(get_db)
):
    """Get specific blast campaign"""
    campaign = db.query(BlastCampaign).filter(
        BlastCampaign.id == campaign_id,
        BlastCampaign.user_id == current_user.id
    ).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return campaign


@app.put("/campaigns/{campaign_id}", response_model=BlastCampaignResponse)
async def update_blast_campaign(
    campaign_id: int,
    campaign_update: BlastCampaignUpdate,
    current_user: User = Depends(RequirePermission("blast:update")),
    db: Session = Depends(get_db)
):
    """Update blast campaign"""
    campaign = db.query(BlastCampaign).filter(
        BlastCampaign.id == campaign_id,
        BlastCampaign.user_id == current_user.id
    ).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update draft campaigns"
        )
    
    if campaign_update.name:
        campaign.name = campaign_update.name
    if campaign_update.message:
        campaign.message = campaign_update.message
    if campaign_update.recipient_list:
        campaign.recipient_list = campaign_update.recipient_list
    if campaign_update.media_url:
        campaign.media_url = campaign_update.media_url
    if campaign_update.scheduled_at:
        campaign.scheduled_at = campaign_update.scheduled_at
        campaign.status = "scheduled"
    
    db.commit()
    db.refresh(campaign)
    return campaign


@app.delete("/campaigns/{campaign_id}", response_model=MessageResponse)
async def delete_blast_campaign(
    campaign_id: int,
    current_user: User = Depends(RequirePermission("blast:delete")),
    db: Session = Depends(get_db)
):
    """Delete blast campaign"""
    campaign = db.query(BlastCampaign).filter(
        BlastCampaign.id == campaign_id,
        BlastCampaign.user_id == current_user.id
    ).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    db.delete(campaign)
    db.commit()
    
    return MessageResponse(message="Campaign deleted successfully")


@app.post("/campaigns/{campaign_id}/send", response_model=MessageResponse)
async def send_blast_campaign(
    campaign_id: int,
    current_user: User = Depends(RequirePermission("blast:send")),
    db: Session = Depends(get_db)
):
    """Send blast campaign immediately"""
    campaign = db.query(BlastCampaign).filter(
        BlastCampaign.id == campaign_id,
        BlastCampaign.user_id == current_user.id
    ).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign.status not in ["draft", "scheduled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign cannot be sent"
        )
    
    campaign.status = "sending"
    db.commit()
    
    # In production, this would trigger a background task
    return MessageResponse(message="Campaign sending started")


@app.post("/media/upload", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    current_user: User = Depends(RequirePermission("blast:with_media")),
):
    """Upload media file (image/video/document) for blast campaigns"""
    import uuid
    import os
    
    allowed_types = {
        "image/jpeg": "image",
        "image/png": "image",
        "image/gif": "image",
        "video/mp4": "video",
        "application/pdf": "document",
    }
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not supported. Allowed: image, video, pdf"
        )
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "bin"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Save file (in production, use S3 or cloud storage)
    upload_dir = "/tmp/media_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    media_url = f"/media/{unique_filename}"
    media_type = allowed_types[file.content_type]
    
    return MediaUploadResponse(
        media_url=media_url,
        media_type=media_type,
        file_name=file.filename,
        file_size=len(content)
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
