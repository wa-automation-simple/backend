"""Service layer for WhatsApp account business logic."""

from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from datetime import datetime, timedelta

from whatsapp.repositories.account_repo import WhatsAppAccountRepository, WarmupScheduleRepository, MessageLogRepository
from whatsapp.models.whatsapp_account import WhatsAppAccount, AccountStatus


class WhatsAppAccountService:
    """Service layer for WhatsApp account operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.account_repo = WhatsAppAccountRepository(db)
        self.warmup_repo = WarmupScheduleRepository(db)
        self.message_repo = MessageLogRepository(db)
    
    def create_account(self, user_id: int, phone_number: str, account_name: str = None, is_primary: bool = False) -> WhatsAppAccount:
        """Create a new WhatsApp account."""
        # Check if phone already exists
        existing = self.account_repo.get_by_phone(phone_number)
        if existing:
            raise ValueError("Phone number already registered")
        
        return self.account_repo.create(user_id, phone_number, account_name, is_primary)
    
    def get_account(self, account_id: int) -> Optional[WhatsAppAccount]:
        """Get account by ID."""
        return self.account_repo.get_by_id(account_id)
    
    def get_user_accounts(self, user_id: int) -> List[WhatsAppAccount]:
        """Get all accounts for a user."""
        return self.account_repo.get_by_user(user_id)
    
    def update_account(self, account_id: int, **kwargs) -> Optional[WhatsAppAccount]:
        """Update account information."""
        return self.account_repo.update(account_id, **kwargs)
    
    def delete_account(self, account_id: int) -> bool:
        """Delete an account."""
        return self.account_repo.delete(account_id)
    
    def list_accounts(
        self,
        user_id: Optional[int] = None,
        status: Optional[AccountStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[WhatsAppAccount], int]:
        """List accounts with filters."""
        return self.account_repo.list_accounts(user_id, status, page, page_size)
    
    def start_warmup(self, account_id: int, duration_days: int = 30) -> dict:
        """Start warmup process for an account."""
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        
        if account.status == AccountStatus.WARMING_UP:
            raise ValueError("Warmup already in progress")
        
        # Generate 30-day warmup schedule
        # Progressive increase: day 1 = 10 msgs, day 30 = 300 msgs
        for day in range(1, duration_days + 1):
            daily_limit = int(10 + (290 * (day / duration_days)))  # Progressive increase
            interval_min = max(60, 300 - (5 * day))  # Decrease interval over time
            interval_max = max(120, 600 - (10 * day))
            
            self.warmup_repo.create_schedule(account_id, day, daily_limit, interval_min, interval_max)
        
        # Update account status
        self.account_repo.set_status(account_id, AccountStatus.WARMING_UP)
        
        return {
            "message": "Warmup started",
            "account_id": account_id,
            "duration_days": duration_days
        }
    
    def get_warmup_status(self, account_id: int) -> Optional[dict]:
        """Get current warmup status."""
        schedule = self.warmup_repo.get_by_account(account_id)
        account = self.account_repo.get_by_id(account_id)
        
        if not schedule or not account:
            return None
        
        # Count messages sent today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        messages_today = self.db.query(MessageLog).filter(
            MessageLog.account_id == account_id,
            MessageLog.created_at >= today_start,
            MessageLog.status.in_(["sent", "delivered", "read"])
        ).count()
        
        progress = (schedule.day / 30) * 100
        
        return {
            "account_id": account_id,
            "current_day": schedule.day,
            "total_days": 30,
            "daily_limit": schedule.daily_limit,
            "messages_sent_today": messages_today,
            "is_completed": schedule.is_completed,
            "progress_percentage": round(progress, 2)
        }
    
    def complete_warmup_day(self, account_id: int) -> bool:
        """Mark current warmup day as completed and move to next day."""
        schedule = self.warmup_repo.get_by_account(account_id)
        if not schedule:
            return False
        
        if schedule.day < 30:
            # Move to next day
            self.warmup_repo.update_day(schedule.id, schedule.day + 1)
        else:
            # Warmup completed
            self.warmup_repo.complete_schedule(account_id)
            self.account_repo.set_status(account_id, AccountStatus.READY)
        
        return True
    
    def send_message(self, account_id: int, recipient: str, content: str, message_type: str = "text", media_url: str = None) -> dict:
        """Send a message (placeholder - actual sending via WhatsApp API)."""
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        
        if account.status not in [AccountStatus.ACTIVE, AccountStatus.READY]:
            raise ValueError(f"Account not ready. Current status: {account.status}")
        
        # Create message log
        log = self.message_repo.create_log(account_id, recipient, message_type, content, media_url)
        
        # TODO: Integrate with actual WhatsApp API (e.g., whatsapp-web.js, Baileys)
        # For now, mark as sent
        self.message_repo.update_status(log.id, "sent")
        
        return {
            "message_id": log.id,
            "status": "sent",
            "recipient": recipient
        }
    
    def get_message_logs(self, account_id: int, page: int = 1, page_size: int = 50) -> Tuple[List, int]:
        """Get message logs for an account."""
        return self.message_repo.get_by_account(account_id, page, page_size)
