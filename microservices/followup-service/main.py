"""
Follow-up Service - Member follow-up tracking and scheduling
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from shared.utils.database import get_db, engine, Base
from shared.schemas.serializers import (
    FollowUpCreate, FollowUpResponse, FollowUpUpdate, MessageResponse
)
from shared.models.tables import User, FollowUp, WhatsAppAccount
from shared.models.rbac import RequirePermission

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Follow-up Service",
    description="Member Follow-up Tracking and Scheduling",
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
    return {"status": "healthy", "service": "followup-service"}


@app.post("/followups", response_model=FollowUpResponse)
async def create_followup(
    followup_data: FollowUpCreate,
    current_user: User = Depends(RequirePermission("followup:create")),
    db: Session = Depends(get_db)
):
    """Create new follow-up for member"""
    # Verify WhatsApp account belongs to user
    wa_account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == followup_data.whatsapp_account_id,
        WhatsAppAccount.user_id == current_user.id
    ).first()
    if not wa_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    
    followup = FollowUp(
        user_id=current_user.id,
        whatsapp_account_id=followup_data.whatsapp_account_id,
        contact_phone=followup_data.contact_phone,
        contact_name=followup_data.contact_name,
        message=followup_data.message,
        scheduled_at=followup_data.scheduled_at,
        notes=followup_data.notes,
        status="pending"
    )
    
    db.add(followup)
    db.commit()
    db.refresh(followup)
    return followup


@app.get("/followups", response_model=List[FollowUpResponse])
async def list_followups(
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(RequirePermission("followup:read")),
    db: Session = Depends(get_db)
):
    """List all follow-ups for current user"""
    query = db.query(FollowUp).filter(FollowUp.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(FollowUp.status == status_filter)
    
    followups = query.offset(skip).limit(limit).all()
    return followups


@app.get("/followups/{followup_id}", response_model=FollowUpResponse)
async def get_followup(
    followup_id: int,
    current_user: User = Depends(RequirePermission("followup:read")),
    db: Session = Depends(get_db)
):
    """Get specific follow-up"""
    followup = db.query(FollowUp).filter(
        FollowUp.id == followup_id,
        FollowUp.user_id == current_user.id
    ).first()
    if not followup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up not found"
        )
    return followup


@app.put("/followups/{followup_id}", response_model=FollowUpResponse)
async def update_followup(
    followup_id: int,
    followup_update: FollowUpUpdate,
    current_user: User = Depends(RequirePermission("followup:update")),
    db: Session = Depends(get_db)
):
    """Update follow-up"""
    followup = db.query(FollowUp).filter(
        FollowUp.id == followup_id,
        FollowUp.user_id == current_user.id
    ).first()
    if not followup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up not found"
        )
    
    if followup_update.contact_name:
        followup.contact_name = followup_update.contact_name
    if followup_update.message:
        followup.message = followup_update.message
    if followup_update.scheduled_at:
        followup.scheduled_at = followup_update.scheduled_at
    if followup_update.notes:
        followup.notes = followup_update.notes
    if followup_update.status:
        followup.status = followup_update.status
        if followup_update.status == "completed":
            followup.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(followup)
    return followup


@app.delete("/followups/{followup_id}", response_model=MessageResponse)
async def delete_followup(
    followup_id: int,
    current_user: User = Depends(RequirePermission("followup:delete")),
    db: Session = Depends(get_db)
):
    """Delete follow-up"""
    followup = db.query(FollowUp).filter(
        FollowUp.id == followup_id,
        FollowUp.user_id == current_user.id
    ).first()
    if not followup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up not found"
        )
    
    db.delete(followup)
    db.commit()
    return MessageResponse(message="Follow-up deleted successfully")


@app.post("/followups/{followup_id}/execute", response_model=MessageResponse)
async def execute_followup(
    followup_id: int,
    current_user: User = Depends(RequirePermission("followup:execute")),
    db: Session = Depends(get_db)
):
    """Execute/send follow-up message"""
    followup = db.query(FollowUp).filter(
        FollowUp.id == followup_id,
        FollowUp.user_id == current_user.id
    ).first()
    if not followup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up not found"
        )
    
    if followup.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending follow-ups can be executed"
        )
    
    # In production, this would send the actual WhatsApp message
    followup.status = "sent"
    followup.completed_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message=f"Follow-up sent to {followup.contact_phone}")


@app.get("/followups/pending/overdue", response_model=List[FollowUpResponse])
async def get_overdue_followups(
    current_user: User = Depends(RequirePermission("followup:read")),
    db: Session = Depends(get_db)
):
    """Get overdue follow-ups"""
    now = datetime.utcnow()
    followups = db.query(FollowUp).filter(
        FollowUp.user_id == current_user.id,
        FollowUp.status == "pending",
        FollowUp.scheduled_at < now
    ).all()
    return followups


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
