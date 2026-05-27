"""Repository for WhatsApp account operations."""

from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional, List, Tuple
from datetime import datetime

from whatsapp.models.whatsapp_account import WhatsAppAccount, WarmupSchedule, MessageLog, AccountStatus


class WhatsAppAccountRepository:
    """Repository for WhatsAppAccount model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, phone_number: str, account_name: str = None, is_primary: bool = False) -> WhatsAppAccount:
        """Create a new WhatsApp account."""
        # If primary, unset other primary accounts for this user
        if is_primary:
            self.db.query(WhatsAppAccount).filter(
                WhatsAppAccount.user_id == user_id,
                WhatsAppAccount.is_primary == True
            ).update({"is_primary": False})
        
        account = WhatsAppAccount(
            user_id=user_id,
            phone_number=phone_number,
            account_name=account_name,
            is_primary=is_primary
        )
        
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account
    
    def get_by_id(self, account_id: int) -> Optional[WhatsAppAccount]:
        """Get account by ID."""
        return self.db.query(WhatsAppAccount).filter(WhatsAppAccount.id == account_id).first()
    
    def get_by_phone(self, phone_number: str) -> Optional[WhatsAppAccount]:
        """Get account by phone number."""
        return self.db.query(WhatsAppAccount).filter(WhatsAppAccount.phone_number == phone_number).first()
    
    def get_by_user(self, user_id: int) -> List[WhatsAppAccount]:
        """Get all accounts for a user."""
        return self.db.query(WhatsAppAccount).filter(WhatsAppAccount.user_id == user_id).all()
    
    def update(self, account_id: int, **kwargs) -> Optional[WhatsAppAccount]:
        """Update account fields."""
        account = self.get_by_id(account_id)
        if not account:
            return None
        
        for key, value in kwargs.items():
            if hasattr(account, key) and value is not None:
                setattr(account, key, value)
        
        account.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(account)
        return account
    
    def delete(self, account_id: int) -> bool:
        """Delete an account."""
        account = self.get_by_id(account_id)
        if not account:
            return False
        
        self.db.delete(account)
        self.db.commit()
        return True
    
    def list_accounts(
        self,
        user_id: Optional[int] = None,
        status: Optional[AccountStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[WhatsAppAccount], int]:
        """List accounts with filters and pagination."""
        query = select(WhatsAppAccount)
        
        if user_id:
            query = query.where(WhatsAppAccount.user_id == user_id)
        if status:
            query = query.where(WhatsAppAccount.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        accounts = self.db.execute(query).scalars().all()
        return list(accounts), total
    
    def set_status(self, account_id: int, status: AccountStatus) -> Optional[WhatsAppAccount]:
        """Update account status."""
        return self.update(account_id, status=status)
    
    def update_session(self, account_id: int, session_data: str) -> Optional[WhatsAppAccount]:
        """Update session data."""
        return self.update(account_id, session_data=session_data, last_active=datetime.utcnow())


class WarmupScheduleRepository:
    """Repository for WarmupSchedule model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_schedule(self, account_id: int, day: int, daily_limit: int, interval_min: int, interval_max: int) -> WarmupSchedule:
        """Create a warmup schedule entry."""
        schedule = WarmupSchedule(
            account_id=account_id,
            day=day,
            daily_limit=daily_limit,
            interval_min=interval_min,
            interval_max=interval_max
        )
        
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule
    
    def get_by_account(self, account_id: int) -> Optional[WarmupSchedule]:
        """Get current warmup schedule for an account."""
        return self.db.query(WarmupSchedule).filter(
            WarmupSchedule.account_id == account_id,
            WarmupSchedule.is_completed == False
        ).first()
    
    def update_day(self, schedule_id: int, day: int) -> Optional[WarmupSchedule]:
        """Update current day."""
        schedule = self.db.query(WarmupSchedule).filter(WarmupSchedule.id == schedule_id).first()
        if not schedule:
            return None
        
        schedule.day = day
        self.db.commit()
        self.db.refresh(schedule)
        return schedule
    
    def complete_schedule(self, account_id: int) -> bool:
        """Mark warmup schedule as completed."""
        schedule = self.get_by_account(account_id)
        if not schedule:
            return False
        
        schedule.is_completed = True
        schedule.completed_at = datetime.utcnow()
        self.db.commit()
        return True


class MessageLogRepository:
    """Repository for MessageLog model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_log(self, account_id: int, recipient: str, message_type: str, content: str = None, media_url: str = None) -> MessageLog:
        """Create a message log entry."""
        log = MessageLog(
            account_id=account_id,
            recipient=recipient,
            message_type=message_type,
            content=content,
            media_url=media_url
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def update_status(self, log_id: int, status: str, error_message: str = None) -> Optional[MessageLog]:
        """Update message status."""
        log = self.db.query(MessageLog).filter(MessageLog.id == log_id).first()
        if not log:
            return None
        
        log.status = status
        if error_message:
            log.error_message = error_message
        
        if status == "sent":
            log.sent_at = datetime.utcnow()
        elif status == "delivered":
            log.delivered_at = datetime.utcnow()
        elif status == "read":
            log.read_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def get_by_account(self, account_id: int, page: int = 1, page_size: int = 50) -> Tuple[List[MessageLog], int]:
        """Get message logs for an account."""
        query = select(MessageLog).where(MessageLog.account_id == account_id)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(MessageLog.created_at.desc())
        
        logs = self.db.execute(query).scalars().all()
        return list(logs), total
