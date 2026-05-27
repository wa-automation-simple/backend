"""WhatsApp Service - Complete implementation with all routes."""
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from .config import settings
from .core.database import Base, engine, get_db
from .models.account import WhatsAppAccount, WarmupSchedule, AccountStatus
from .schemas.serializers import (
    WhatsAppAccountCreate, WhatsAppAccountResponse,
    WarmupStart, WarmupStatus, QRCodeResponse, RecoveryLinkResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.SERVICE_VERSION,
    description="WhatsApp Management Service for Marketing SaaS"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Account Routes ============

@app.post("/accounts", response_model=WhatsAppAccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account_data: WhatsAppAccountCreate,
    db: Session = Depends(get_db),
    user_id: int = 1  # From JWT token in production
):
    """Create new WhatsApp account."""
    # Check if phone already exists
    existing = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.phone_number == account_data.phone_number
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Create account
    account = WhatsAppAccount(
        user_id=user_id,
        phone_number=account_data.phone_number,
        display_name=account_data.display_name,
        is_primary=account_data.is_primary
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return account


@app.get("/accounts", response_model=List[WhatsAppAccountResponse])
def list_accounts(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[AccountStatus] = None,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """List all WhatsApp accounts for user."""
    query = db.query(WhatsAppAccount).filter(WhatsAppAccount.user_id == user_id)
    
    if status_filter:
        query = query.filter(WhatsAppAccount.status == status_filter)
    
    accounts = query.offset(skip).limit(limit).all()
    return accounts


@app.get("/accounts/{account_id}", response_model=WhatsAppAccountResponse)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """Get specific WhatsApp account."""
    account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == account_id,
        WhatsAppAccount.user_id == user_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    return account


@app.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """Delete WhatsApp account."""
    account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == account_id,
        WhatsAppAccount.user_id == user_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    db.delete(account)
    db.commit()
    
    return None


# ============ QR Code & Connection Routes ============

@app.post("/accounts/{account_id}/qr", response_model=QRCodeResponse)
def generate_qr(
    account_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """Generate QR code for WhatsApp connection."""
    account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == account_id,
        WhatsAppAccount.user_id == user_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    # Generate QR code (mock implementation)
    qr_code = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    account.qr_code = qr_code
    account.status = AccountStatus.DISCONNECTED
    db.commit()
    
    return QRCodeResponse(
        account_id=account_id,
        qr_code=qr_code,
        expires_in=60  # 60 seconds
    )


# ============ Warmup Routes ============

@app.post("/accounts/{account_id}/warmup/start", response_model=WarmupStatus)
def start_warmup(
    account_id: int,
    warmup_data: WarmupStart,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """Start warming up WhatsApp account."""
    from datetime import datetime, timedelta
    
    account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == account_id,
        WhatsAppAccount.user_id == user_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    # Check if warmup already exists
    existing_warmup = db.query(WarmupSchedule).filter(
        WarmupSchedule.account_id == account_id
    ).first()
    
    if existing_warmup and existing_warmup.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Warmup already in progress"
        )
    
    # Create or update warmup schedule
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=warmup_data.total_days)
    
    if existing_warmup:
        existing_warmup.total_days = warmup_data.total_days
        existing_warmup.day_1_limit = warmup_data.day_1_limit
        existing_warmup.daily_increment = warmup_data.daily_increment
        existing_warmup.max_daily_limit = warmup_data.max_daily_limit
        existing_warmup.start_date = start_date
        existing_warmup.end_date = end_date
        existing_warmup.current_day = 0
        existing_warmup.today_limit = warmup_data.day_1_limit
        existing_warmup.is_active = True
        existing_warmup.is_completed = False
        warmup = existing_warmup
    else:
        warmup = WarmupSchedule(
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
            total_days=warmup_data.total_days,
            day_1_limit=warmup_data.day_1_limit,
            daily_increment=warmup_data.daily_increment,
            max_daily_limit=warmup_data.max_daily_limit,
            today_limit=warmup_data.day_1_limit,
            is_active=True
        )
        db.add(warmup)
    
    # Update account status
    account.status = AccountStatus.WARMING_UP
    db.commit()
    db.refresh(warmup)
    
    return WarmupStatus(
        account_id=account_id,
        current_day=warmup.current_day,
        total_days=warmup.total_days,
        today_limit=warmup.today_limit,
        messages_sent_today=warmup.messages_sent_today,
        is_active=warmup.is_active,
        is_completed=warmup.is_completed,
        start_date=warmup.start_date,
        end_date=warmup.end_date
    )


@app.get("/accounts/{account_id}/warmup/status", response_model=WarmupStatus)
def get_warmup_status(
    account_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """Get warmup status for account."""
    warmup = db.query(WarmupSchedule).filter(
        WarmupSchedule.account_id == account_id
    ).first()
    
    if not warmup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No warmup schedule found"
        )
    
    return WarmupStatus(
        account_id=account_id,
        current_day=warmup.current_day,
        total_days=warmup.total_days,
        today_limit=warmup.today_limit,
        messages_sent_today=warmup.messages_sent_today,
        is_active=warmup.is_active,
        is_completed=warmup.is_completed,
        start_date=warmup.start_date,
        end_date=warmup.end_date
    )


# ============ Recovery Routes ============

@app.post("/accounts/{account_id}/recovery/link", response_model=RecoveryLinkResponse)
def get_recovery_link(
    account_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """Get recovery link for banned account."""
    account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == account_id,
        WhatsAppAccount.user_id == user_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    # Generate recovery link (mock)
    recovery_link = f"https://wa.me/recovery?account={account_id}&token=abc123"
    
    account.status = AccountStatus.RECOVERING
    db.commit()
    
    return RecoveryLinkResponse(
        account_id=account_id,
        recovery_link=recovery_link,
        auto_click_enabled=False
    )


@app.post("/accounts/{account_id}/recovery/auto-click/enable")
def enable_auto_click(
    account_id: int,
    interval_seconds: int = 30,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """Enable auto-click for recovery link."""
    # This would integrate with the session model
    return {
        "message": "Auto-click enabled",
        "account_id": account_id,
        "interval_seconds": interval_seconds
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
