"""
Blast Service - Bulk messaging with image support
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio
import random

from shared.database import get_db
from shared.models import BlastCampaign, WhatsAppAccount, User
from shared.schemas import BlastCampaignCreate, BlastCampaignResponse
from shared.config import settings

app = FastAPI(title="Blast Service", version="1.0.0")


class BlastManager:
    """Manage bulk message campaigns"""
    
    def __init__(self):
        self.active_campaigns = {}
    
    async def send_batch(
        self,
        campaign_id: int,
        recipients: List[str],
        message: str,
        media_url: Optional[str] = None,
        whatsapp_session=None
    ):
        """Send messages to a batch of recipients"""
        results = []
        
        for recipient in recipients:
            # Simulate sending with random delay
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            result = {
                "recipient": recipient,
                "success": random.choice([True, True, True, False]),  # 75% success rate simulation
                "message_id": f"msg_{random.randint(100000, 999999)}"
            }
            results.append(result)
        
        return results


blast_manager = BlastManager()


@app.post("/campaigns", response_model=BlastCampaignResponse)
async def create_campaign(
    campaign_data: BlastCampaignCreate,
    db: Session = Depends(get_db)
):
    """Create a new blast campaign"""
    # Verify WhatsApp account exists
    wa_account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == campaign_data.whatsapp_account_id
    ).first()
    if not wa_account:
        raise HTTPException(status_code=404, detail="WhatsApp account not found")
    
    db_campaign = BlastCampaign(
        user_id=1,  # Would come from JWT token
        whatsapp_account_id=campaign_data.whatsapp_account_id,
        name=campaign_data.name,
        message_text=campaign_data.message_text,
        media_url=campaign_data.media_url,
        media_type=campaign_data.media_type,
        recipients=campaign_data.recipients,
        scheduled_at=campaign_data.scheduled_at,
        status="scheduled" if campaign_data.scheduled_at else "draft"
    )
    
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    
    return db_campaign


@app.get("/campaigns", response_model=List[BlastCampaignResponse])
async def list_campaigns(
    user_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all campaigns for a user"""
    query = db.query(BlastCampaign).filter(BlastCampaign.user_id == user_id)
    
    if status:
        query = query.filter(BlastCampaign.status == status)
    
    campaigns = query.all()
    return campaigns


@app.get("/campaigns/{campaign_id}", response_model=BlastCampaignResponse)
async def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Get campaign details"""
    campaign = db.query(BlastCampaign).filter(BlastCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign


@app.post("/campaigns/{campaign_id}/send")
async def send_campaign(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start sending a campaign"""
    campaign = db.query(BlastCampaign).filter(BlastCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status not in ["draft", "scheduled"]:
        raise HTTPException(status_code=400, detail=f"Campaign cannot be sent. Status: {campaign.status}")
    
    # Update status
    campaign.status = "sending"
    db.commit()
    
    # Start sending in background
    background_tasks.add_task(
        process_campaign,
        campaign_id,
        campaign.recipients,
        campaign.message_text,
        campaign.media_url,
        campaign.whatsapp_account_id,
        db
    )
    
    return {"status": "sending_started", "campaign_id": campaign_id}


async def process_campaign(
    campaign_id: int,
    recipients: List[str],
    message: str,
    media_url: Optional[str],
    whatsapp_account_id: int,
    db: Session
):
    """Background task to process campaign"""
    campaign = db.query(BlastCampaign).filter(BlastCampaign.id == campaign_id).first()
    if not campaign:
        return
    
    # Get WhatsApp account
    wa_account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == whatsapp_account_id
    ).first()
    
    if not wa_account or wa_account.status != "connected":
        campaign.status = "failed"
        campaign.failed_count = len(recipients)
        db.commit()
        return
    
    # Process in batches of 50
    batch_size = 50
    total_sent = 0
    total_delivered = 0
    total_failed = 0
    
    for i in range(0, len(recipients), batch_size):
        batch = recipients[i:i + batch_size]
        
        results = await blast_manager.send_batch(
            campaign_id=campaign_id,
            recipients=batch,
            message=message,
            media_url=media_url
        )
        
        for result in results:
            if result["success"]:
                total_delivered += 1
            else:
                total_failed += 1
            total_sent += 1
        
        # Update progress
        campaign.sent_count = total_sent
        campaign.delivered_count = total_delivered
        campaign.failed_count = total_failed
        db.commit()
        
        # Delay between batches to avoid rate limiting
        await asyncio.sleep(random.uniform(5, 10))
    
    campaign.status = "completed"
    db.commit()


@app.post("/upload-media")
async def upload_media(
    file: UploadFile = File(...),
    campaign_id: Optional[int] = None
):
    """Upload media file for campaign"""
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "video/mp4"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # In production, upload to S3 or similar
    # For now, just return mock URL
    media_type = "image" if "image" in file.content_type else "video"
    mock_url = f"https://storage.example.com/media/{file.filename}"
    
    return {
        "success": True,
        "media_url": mock_url,
        "media_type": media_type,
        "filename": file.filename,
        "content_type": file.content_type
    }


@app.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Delete a campaign"""
    campaign = db.query(BlastCampaign).filter(BlastCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status == "sending":
        raise HTTPException(status_code=400, detail="Cannot delete active campaign")
    
    db.delete(campaign)
    db.commit()
    
    return {"status": "deleted", "campaign_id": campaign_id}


@app.get("/campaigns/{campaign_id}/stats")
async def get_campaign_stats(campaign_id: int, db: Session = Depends(get_db)):
    """Get campaign statistics"""
    campaign = db.query(BlastCampaign).filter(BlastCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    total = len(campaign.recipients)
    success_rate = (campaign.delivered_count / total * 100) if total > 0 else 0
    
    return {
        "campaign_id": campaign_id,
        "total_recipients": total,
        "sent": campaign.sent_count,
        "delivered": campaign.delivered_count,
        "failed": campaign.failed_count,
        "success_rate": f"{success_rate:.2f}%",
        "status": campaign.status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
