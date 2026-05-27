from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
from whatsapp_service.models.whatsapp import WhatsAppAccount, WarmupLog


def create_whatsapp_account(db: Session, user_id: int, phone_number: str) -> WhatsAppAccount:
    """Create a new WhatsApp account"""
    session_id = f"wa_{user_id}_{uuid.uuid4().hex[:12]}"
    db_account = WhatsAppAccount(
        user_id=user_id,
        phone_number=phone_number,
        session_id=session_id,
        status="disconnected"
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def get_whatsapp_accounts_by_user(db: Session, user_id: int) -> List[WhatsAppAccount]:
    """Get all WhatsApp accounts for a user"""
    return db.query(WhatsAppAccount).filter(WhatsAppAccount.user_id == user_id).all()


def get_whatsapp_account(db: Session, account_id: int, user_id: Optional[int] = None) -> Optional[WhatsAppAccount]:
    """Get WhatsApp account by ID"""
    query = db.query(WhatsAppAccount).filter(WhatsAppAccount.id == account_id)
    if user_id:
        query = query.filter(WhatsAppAccount.user_id == user_id)
    return query.first()


def update_whatsapp_account(db: Session, account_id: int, **kwargs) -> Optional[WhatsAppAccount]:
    """Update WhatsApp account fields"""
    account = db.query(WhatsAppAccount).filter(WhatsAppAccount.id == account_id).first()
    if not account:
        return None
    
    for key, value in kwargs.items():
        if hasattr(account, key):
            setattr(account, key, value)
    
    account.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(account)
    return account


def delete_whatsapp_account(db: Session, account_id: int, user_id: Optional[int] = None) -> bool:
    """Delete WhatsApp account"""
    query = db.query(WhatsAppAccount).filter(WhatsAppAccount.id == account_id)
    if user_id:
        query = query.filter(WhatsAppAccount.user_id == user_id)
    account = query.first()
    if not account:
        return False
    db.delete(account)
    db.commit()
    return True


# Warming functions
WARMUP_SCHEDULE = {
    1: {"min": 5, "max": 10},
    2: {"min": 10, "max": 20},
    3: {"min": 20, "max": 30},
    4: {"min": 30, "max": 40},
    5: {"min": 40, "max": 50},
    6: {"min": 50, "max": 60},
    7: {"min": 60, "max": 70},
    8: {"min": 70, "max": 80},
    9: {"min": 80, "max": 90},
    10: {"min": 90, "max": 100},
    11: {"min": 100, "max": 110},
    12: {"min": 110, "max": 120},
    13: {"min": 120, "max": 130},
    14: {"min": 130, "max": 140},
    15: {"min": 140, "max": 150},
    16: {"min": 150, "max": 160},
    17: {"min": 160, "max": 170},
    18: {"min": 170, "max": 180},
    19: {"min": 180, "max": 190},
    20: {"min": 190, "max": 200},
    21: {"min": 200, "max": 210},
    22: {"min": 210, "max": 220},
    23: {"min": 220, "max": 230},
    24: {"min": 230, "max": 240},
    25: {"min": 240, "max": 250},
    26: {"min": 250, "max": 260},
    27: {"min": 260, "max": 270},
    28: {"min": 270, "max": 280},
    29: {"min": 280, "max": 290},
    30: {"min": 290, "max": 300},
}


def start_warming(db: Session, account_id: int) -> Optional[WhatsAppAccount]:
    """Start warming process for a WhatsApp account"""
    account = get_whatsapp_account(db, account_id)
    if not account:
        return None
    
    account.is_warming = True
    account.warming_day = 1
    account.warming_started_at = datetime.utcnow()
    account.status = "warming"
    
    # Create initial warmup log
    warmup_log = WarmupLog(
        whatsapp_account_id=account_id,
        day=1,
        status="pending"
    )
    db.add(warmup_log)
    db.commit()
    db.refresh(account)
    return account


def stop_warming(db: Session, account_id: int) -> Optional[WhatsAppAccount]:
    """Stop warming process for a WhatsApp account"""
    account = get_whatsapp_account(db, account_id)
    if not account:
        return None
    
    account.is_warming = False
    account.status = "connected"
    db.commit()
    db.refresh(account)
    return account


def get_warming_status(db: Session, account_id: int) -> dict:
    """Get warming status for an account"""
    account = get_whatsapp_account(db, account_id)
    if not account:
        return {}
    
    current_day = account.warming_day
    schedule = WARMUP_SCHEDULE.get(current_day, {"min": 0, "max": 0})
    
    # Get today's log
    today_log = db.query(WarmupLog).filter(
        WarmupLog.whatsapp_account_id == account_id,
        WarmupLog.day == current_day
    ).first()
    
    messages_sent = today_log.messages_sent if today_log else 0
    
    return {
        "whatsapp_account_id": account_id,
        "day": current_day,
        "messages_sent_today": messages_sent,
        "messages_limit": schedule["max"],
        "status": account.status,
        "is_warming": account.is_warming
    }


def increment_warming_day(db: Session, account_id: int) -> Optional[WhatsAppAccount]:
    """Increment warming day"""
    account = get_whatsapp_account(db, account_id)
    if not account or not account.is_warming:
        return None
    
    if account.warming_day < 30:
        account.warming_day += 1
        
        # Create new warmup log
        warmup_log = WarmupLog(
            whatsapp_account_id=account_id,
            day=account.warming_day,
            status="pending"
        )
        db.add(warmup_log)
        
        if account.warming_day == 30:
            account.is_warming = False
            account.status = "connected"
        
        db.commit()
        db.refresh(account)
    
    return account


def set_recovery_link(db: Session, account_id: int, recovery_link: str) -> Optional[WhatsAppAccount]:
    """Set recovery link for banned account"""
    return update_whatsapp_account(db, account_id, recovery_link=recovery_link, status="banned")
