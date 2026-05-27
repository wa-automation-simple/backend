"""
WhatsApp Service - WhatsApp account management, warming, multi-account support
"""
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from shared.utils.database import get_db, engine, Base
from shared.schemas.serializers import (
    WhatsAppAccountCreate, WhatsAppAccountResponse, WhatsAppAccountUpdate,
    WarmupStart, WarmupStatus, MessageResponse
)
from shared.models.tables import User, WhatsAppAccount
from shared.utils.auth import get_current_user
from shared.models.rbac import RequirePermission

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WhatsApp Service",
    description="WhatsApp Account Management, Warming, Multi-Account Support",
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
    return {"status": "healthy", "service": "whatsapp-service"}


@app.post("/accounts", response_model=WhatsAppAccountResponse)
async def create_whatsapp_account(
    account_data: WhatsAppAccountCreate,
    current_user: User = Depends(RequirePermission("wa_account:create")),
    db: Session = Depends(get_db)
):
    """Add new WhatsApp account (multi-account support)"""
    # Check if phone already exists
    existing = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.phone_number == account_data.phone_number
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    new_account = WhatsAppAccount(
        user_id=current_user.id,
        phone_number=account_data.phone_number,
        status="disconnected"
    )
    
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    
    return new_account


@app.get("/accounts", response_model=List[WhatsAppAccountResponse])
async def list_whatsapp_accounts(
    current_user: User = Depends(RequirePermission("wa_account:read")),
    db: Session = Depends(get_db)
):
    """List all WhatsApp accounts for current user"""
    accounts = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.user_id == current_user.id
    ).all()
    return accounts


@app.get("/accounts/{account_id}", response_model=WhatsAppAccountResponse)
async def get_whatsapp_account(
    account_id: int,
    current_user: User = Depends(RequirePermission("wa_account:read")),
    db: Session = Depends(get_db)
):
    """Get specific WhatsApp account"""
    account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == account_id,
        WhatsAppAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    return account


@app.put("/accounts/{account_id}", response_model=WhatsAppAccountResponse)
async def update_whatsapp_account(
    account_id: int,
    account_update: WhatsAppAccountUpdate,
    current_user: User = Depends(RequirePermission("wa_account:update")),
    db: Session = Depends(get_db)
):
    """Update WhatsApp account settings"""
    account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == account_id,
        WhatsAppAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    
    if account_update.auto_click_recovery is not None:
        account.auto_click_recovery = account_update.auto_click_recovery
    
    if account_update.recovery_link is not None:
        account.recovery_link = account_update.recovery_link
    
    db.commit()
    db.refresh(account)
    return account


@app.delete("/accounts/{account_id}", response_model=MessageResponse)
async def delete_whatsapp_account(
    account_id: int,
    current_user: User = Depends(RequirePermission("wa_account:delete")),
    db: Session = Depends(get_db)
):
    """Delete WhatsApp account"""
    account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == account_id,
        WhatsAppAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    
    db.delete(account)
    db.commit()
    
    return MessageResponse(message="WhatsApp account deleted successfully")


@app.post("/warmup/start", response_model=MessageResponse)
async def start_warmup(
    warmup_data: WarmupStart,
    current_user: User = Depends(RequirePermission("wa_warmup:manage")),
    db: Session = Depends(get_db)
):
    """Start WhatsApp warming process"""
    from datetime import datetime
    
    account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == warmup_data.whatsapp_account_id,
        WhatsAppAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    
    account.is_warming = True
    account.warmup_day = 1
    account.warmup_started_at = datetime.utcnow()
    account.status = "warming"
    
    db.commit()
    
    return MessageResponse(message="Warmup started successfully")


@app.get("/warmup/status/{account_id}", response_model=WarmupStatus)
async def get_warmup_status(
    account_id: int,
    current_user: User = Depends(RequirePermission("wa_warmup:manage")),
    db: Session = Depends(get_db)
):
    """Get warmup status for WhatsApp account"""
    account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == account_id,
        WhatsAppAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    
    return WarmupStatus(
        whatsapp_account_id=account.id,
        is_warming=account.is_warming,
        current_day=account.warmup_day,
        total_days=30,
        messages_sent_today=0,
        next_message_at=None
    )


@app.post("/accounts/{account_id}/recovery-link", response_model=MessageResponse)
async def generate_recovery_link(
    account_id: int,
    current_user: User = Depends(RequirePermission("recovery:manage")),
    db: Session = Depends(get_db)
):
    """Generate recovery link for banned WhatsApp account"""
    import uuid
    from datetime import datetime, timedelta
    
    account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == account_id,
        WhatsAppAccount.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    
    # Generate unique recovery link
    recovery_token = str(uuid.uuid4())
    account.recovery_link = f"https://wa.me/recovery/{recovery_token}"
    account.auto_click_recovery = True
    account.status = "banned"
    
    db.commit()
    
    return MessageResponse(
        message=f"Recovery link generated: {account.recovery_link}"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
