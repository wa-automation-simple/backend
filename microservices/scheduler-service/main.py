"""
Scheduler Service - Background task scheduling for warmup, blast, followups
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from shared.utils.database import get_db, engine, Base
from shared.models.tables import (
    WhatsAppAccount, BlastCampaign, FollowUp, WarmupSchedule
)
from shared.models.rbac import RequirePermission, Role
from shared.schemas.serializers import MessageResponse

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Scheduler Service",
    description="Background Task Scheduling for Warmup, Blast, and Follow-ups",
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
    return {"status": "healthy", "service": "scheduler-service"}


# ============== WARMUP SCHEDULER ==============

@app.post("/warmup/execute/{account_id}")
async def execute_warmup_task(
    account_id: int,
    db: Session = Depends(get_db)
):
    """Execute daily warmup task for WhatsApp account"""
    account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == account_id,
        WhatsAppAccount.is_warming == True
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warming account not found"
        )
    
    # Get warmup schedule for current day
    schedule = db.query(WarmupSchedule).filter(
        WarmupSchedule.day == account.warmup_day
    ).first()
    
    if not schedule:
        # Default schedule
        messages_to_send = min(5 + account.warmup_day, 50)
    else:
        messages_to_send = (schedule.messages_min + schedule.messages_max) // 2
    
    # In production, this would send actual warmup messages
    # Increment day after completing daily tasks
    account.warmup_day += 1
    
    if account.warmup_day > 30:
        account.is_warming = False
        account.status = "connected"
    
    db.commit()
    
    return {
        "account_id": account_id,
        "day": account.warmup_day,
        "messages_sent": messages_to_send,
        "status": account.status
    }


# ============== BLAST SCHEDULER ==============

@app.post("/blast/execute-pending")
async def execute_pending_blasts(
    db: Session = Depends(get_db)
):
    """Execute all pending scheduled blast campaigns"""
    now = datetime.utcnow()
    
    campaigns = db.query(BlastCampaign).filter(
        BlastCampaign.status == "scheduled",
        BlastCampaign.scheduled_at <= now
    ).all()
    
    executed_count = 0
    for campaign in campaigns:
        campaign.status = "sending"
        executed_count += 1
    
    db.commit()
    
    return {
        "executed_count": executed_count,
        "campaigns": [c.id for c in campaigns]
    }


# ============== FOLLOW-UP SCHEDULER ==============

@app.post("/followup/execute-pending")
async def execute_pending_followups(
    db: Session = Depends(get_db)
):
    """Execute all pending scheduled follow-ups"""
    now = datetime.utcnow()
    
    followups = db.query(FollowUp).filter(
        FollowUp.status == "pending",
        FollowUp.scheduled_at <= now
    ).all()
    
    executed_count = 0
    for followup in followups:
        followup.status = "sent"
        followup.completed_at = now
        executed_count += 1
    
    db.commit()
    
    return {
        "executed_count": executed_count,
        "followups": [f.id for f in followups]
    }


# ============== AUTO-CLICK RECOVERY ==============

@app.post("/recovery/auto-click/{account_id}")
async def trigger_auto_click_recovery(
    account_id: int,
    db: Session = Depends(get_db)
):
    """Trigger auto-click on recovery link for banned account"""
    account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == account_id,
        WhatsAppAccount.auto_click_recovery == True,
        WhatsAppAccount.recovery_link != None
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account with recovery link not found"
        )
    
    # In production, this would use Selenium/Puppeteer to auto-click the link
    # For demo, just update status
    account.status = "recovering"
    db.commit()
    
    return {
        "account_id": account_id,
        "recovery_link": account.recovery_link,
        "status": "clicked",
        "message": "Auto-click triggered on recovery link"
    }


# ============== INIT DEFAULT WARMUP SCHEDULES ==============

@app.post("/warmup/init-schedules", response_model=MessageResponse)
async def initialize_warmup_schedules(
    db: Session = Depends(get_db)
):
    """Initialize default warmup schedules (30 days)"""
    # Check if already initialized
    existing = db.query(WarmupSchedule).first()
    if existing:
        return MessageResponse(message="Warmup schedules already initialized")
    
    # Create 30-day warmup schedule
    schedules = []
    for day in range(1, 31):
        schedule = WarmupSchedule(
            day=day,
            messages_min=max(5, day * 2),
            messages_max=max(10, day * 3),
            delay_min_seconds=60,
            delay_max_seconds=300
        )
        schedules.append(schedule)
    
    db.add_all(schedules)
    db.commit()
    
    return MessageResponse(message="Warmup schedules initialized successfully")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
