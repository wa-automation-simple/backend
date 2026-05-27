"""
Follow-up Service - Member follow-up tracking and scheduling
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio

from shared.database import get_db
from shared.models import FollowUp, WhatsAppAccount, User
from shared.schemas import FollowUpCreate, FollowUpResponse
from shared.config import settings

app = FastAPI(title="Follow-up Service", version="1.0.0")


@app.post("/followups", response_model=FollowUpResponse)
async def create_followup(
    followup_data: FollowUpCreate,
    db: Session = Depends(get_db)
):
    """Create a new follow-up task"""
    db_followup = FollowUp(
        user_id=1,  # Would come from JWT
        whatsapp_account_id=followup_data.whatsapp_account_id,
        contact_phone=followup_data.contact_phone,
        contact_name=followup_data.contact_name,
        notes=followup_data.notes,
        next_follow_up=followup_data.next_follow_up or datetime.now() + timedelta(days=1),
        status="pending"
    )
    
    db.add(db_followup)
    db.commit()
    db.refresh(db_followup)
    
    return db_followup


@app.get("/followups", response_model=List[FollowUpResponse])
async def list_followups(
    user_id: int,
    status: Optional[str] = None,
    whatsapp_account_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List all follow-ups for a user"""
    query = db.query(FollowUp).filter(FollowUp.user_id == user_id)
    
    if status:
        query = query.filter(FollowUp.status == status)
    
    if whatsapp_account_id:
        query = query.filter(FollowUp.whatsapp_account_id == whatsapp_account_id)
    
    # Filter upcoming follow-ups
    query = query.order_by(FollowUp.next_follow_up.asc())
    
    followups = query.all()
    return followups


@app.get("/followups/{followup_id}", response_model=FollowUpResponse)
async def get_followup(followup_id: int, db: Session = Depends(get_db)):
    """Get follow-up details"""
    followup = db.query(FollowUp).filter(FollowUp.id == followup_id).first()
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    
    return followup


@app.put("/followups/{followup_id}/complete")
async def complete_followup(
    followup_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Mark a follow-up as completed"""
    followup = db.query(FollowUp).filter(FollowUp.id == followup_id).first()
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    
    followup.status = "completed"
    followup.last_interaction = datetime.now()
    followup.follow_up_count += 1
    
    if notes:
        followup.notes = f"{followup.notes or ''}\n[Completed]: {notes}"
    
    db.commit()
    
    return {
        "status": "completed",
        "followup_id": followup_id,
        "total_interactions": followup.follow_up_count
    }


@app.put("/followups/{followup_id}/reschedule")
async def reschedule_followup(
    followup_id: int,
    days: int = 1,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Reschedule a follow-up"""
    followup = db.query(FollowUp).filter(FollowUp.id == followup_id).first()
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    
    followup.next_follow_up = datetime.now() + timedelta(days=days)
    followup.status = "pending"
    
    if notes:
        followup.notes = f"{followup.notes or ''}\n[Rescheduled]: {notes}"
    
    db.commit()
    
    return {
        "status": "rescheduled",
        "followup_id": followup_id,
        "next_follow_up": followup.next_follow_up
    }


@app.delete("/followups/{followup_id}")
async def delete_followup(followup_id: int, db: Session = Depends(get_db)):
    """Delete a follow-up"""
    followup = db.query(FollowUp).filter(FollowUp.id == followup_id).first()
    if not followup:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    
    db.delete(followup)
    db.commit()
    
    return {"status": "deleted", "followup_id": followup_id}


@app.post("/followups/batch/reminder")
async def send_batch_reminders(
    user_id: int,
    whatsapp_account_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send reminders for pending follow-ups"""
    # Get pending follow-ups that are due
    pending_followups = db.query(FollowUp).filter(
        FollowUp.user_id == user_id,
        FollowUp.status == "pending",
        FollowUp.next_follow_up <= datetime.now()
    ).all()
    
    if not pending_followups:
        return {"status": "no_pending_followups", "count": 0}
    
    # Process in background
    background_tasks.add_task(
        process_followup_reminders,
        pending_followups,
        whatsapp_account_id,
        db
    )
    
    return {
        "status": "processing",
        "count": len(pending_followups)
    }


async def process_followup_reminders(
    followups: List[FollowUp],
    whatsapp_account_id: int,
    db: Session
):
    """Background task to process follow-up reminders"""
    # In production, this would integrate with WhatsApp service
    for followup in followups:
        # Simulate sending reminder
        await asyncio.sleep(0.5)
        
        # Update follow-up
        followup.last_interaction = datetime.now()
        followup.follow_up_count += 1
        db.commit()


@app.get("/followups/stats/{user_id}")
async def get_followup_stats(user_id: int, db: Session = Depends(get_db)):
    """Get follow-up statistics"""
    total = db.query(FollowUp).filter(FollowUp.user_id == user_id).count()
    pending = db.query(FollowUp).filter(
        FollowUp.user_id == user_id,
        FollowUp.status == "pending"
    ).count()
    completed = db.query(FollowUp).filter(
        FollowUp.user_id == user_id,
        FollowUp.status == "completed"
    ).count()
    
    # Get overdue
    overdue = db.query(FollowUp).filter(
        FollowUp.user_id == user_id,
        FollowUp.status == "pending",
        FollowUp.next_follow_up < datetime.now()
    ).count()
    
    return {
        "user_id": user_id,
        "total_followups": total,
        "pending": pending,
        "completed": completed,
        "overdue": overdue,
        "completion_rate": f"{(completed / total * 100) if total > 0 else 0:.2f}%"
    }


@app.get("/followups/upcoming/{user_id}")
async def get_upcoming_followups(
    user_id: int,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get upcoming follow-ups within specified days"""
    upcoming = db.query(FollowUp).filter(
        FollowUp.user_id == user_id,
        FollowUp.status == "pending",
        FollowUp.next_follow_up <= datetime.now() + timedelta(days=days),
        FollowUp.next_follow_up >= datetime.now()
    ).order_by(FollowUp.next_follow_up.asc()).all()
    
    return {
        "count": len(upcoming),
        "days": days,
        "followups": [
            {
                "id": f.id,
                "contact_name": f.contact_name,
                "contact_phone": f.contact_phone,
                "next_follow_up": f.next_follow_up,
                "notes": f.notes
            }
            for f in upcoming
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
