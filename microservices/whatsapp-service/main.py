"""
WhatsApp Service - Multi-account WhatsApp management
Handles: connection, messaging, warming, auto-click recovery
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio
import random

from shared.database import get_db
from shared.models import User, WhatsAppAccount, WarmingSchedule, AutoReply
from shared.schemas import WhatsAppAccountCreate, WhatsAppAccountResponse, MessageSend, MessageResponse
from shared.utils import generate_session_id, get_warming_delays, get_warming_message_limit, generate_recovery_link
from shared.config import settings

app = FastAPI(title="WhatsApp Service", version="1.0.0")

# In-memory session storage (use Redis in production)
active_sessions = {}


class WhatsAppSession:
    """Mock WhatsApp session manager"""
    
    def __init__(self, phone_number: str, session_id: str):
        self.phone_number = phone_number
        self.session_id = session_id
        self.status = "disconnected"
        self.is_warming = False
        
    async def connect(self):
        """Simulate WhatsApp connection"""
        await asyncio.sleep(2)  # Simulate connection time
        self.status = "connected"
        
    async def disconnect(self):
        """Disconnect WhatsApp session"""
        self.status = "disconnected"
        
    async def send_message(self, recipient: str, message: str, media_url: Optional[str] = None) -> dict:
        """Send a message"""
        if self.status != "connected":
            raise HTTPException(status_code=400, detail="WhatsApp not connected")
        
        # Simulate sending
        await asyncio.sleep(0.5)
        return {
            "success": True,
            "message_id": f"msg_{random.randint(100000, 999999)}",
            "status": "sent"
        }
    
    async def click_link(self, url: str) -> bool:
        """Auto-click recovery link"""
        # Simulate clicking a link
        await asyncio.sleep(1)
        return True


@app.post("/accounts", response_model=WhatsAppAccountResponse)
async def create_account(
    account_data: WhatsAppAccountCreate,
    current_user: dict,  # Would be validated via JWT in production
    db: Session = Depends(get_db)
):
    """Add a new WhatsApp account"""
    # Check if phone number already exists
    existing = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.phone_number == account_data.phone_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    session_id = generate_session_id()
    db_account = WhatsAppAccount(
        user_id=current_user.get("user_id", 1),
        phone_number=account_data.phone_number,
        session_id=session_id,
        status="disconnected"
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return db_account


@app.get("/accounts", response_model=List[WhatsAppAccountResponse])
async def list_accounts(
    user_id: int,
    db: Session = Depends(get_db)
):
    """List all WhatsApp accounts for a user"""
    accounts = db.query(WhatsAppAccount).filter(WhatsAppAccount.user_id == user_id).all()
    return accounts


@app.post("/accounts/{account_id}/connect")
async def connect_account(account_id: int, db: Session = Depends(get_db)):
    """Connect a WhatsApp account"""
    account = db.query(WhatsAppAccount).filter(WhatsAppAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Create session
    session = WhatsAppSession(account.phone_number, account.session_id)
    await session.connect()
    active_sessions[account.session_id] = session
    
    account.status = "connected"
    account.last_active = asyncio.get_event_loop().time()
    db.commit()
    
    return {"status": "connected", "session_id": account.session_id}


@app.post("/accounts/{account_id}/disconnect")
async def disconnect_account(account_id: int, db: Session = Depends(get_db)):
    """Disconnect a WhatsApp account"""
    account = db.query(WhatsAppAccount).filter(WhatsAppAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.session_id in active_sessions:
        await active_sessions[account.session_id].disconnect()
        del active_sessions[account.session_id]
    
    account.status = "disconnected"
    db.commit()
    
    return {"status": "disconnected"}


@app.post("/messages/send", response_model=MessageResponse)
async def send_message(
    message_data: MessageSend,
    db: Session = Depends(get_db)
):
    """Send a WhatsApp message"""
    account = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.id == message_data.whatsapp_account_id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.status != "connected":
        raise HTTPException(status_code=400, detail="WhatsApp account not connected")
    
    session = active_sessions.get(account.session_id)
    if not session:
        raise HTTPException(status_code=400, detail="No active session")
    
    result = await session.send_message(
        recipient=message_data.recipient,
        message=message_data.message,
        media_url=message_data.media_url
    )
    
    return MessageResponse(**result)


@app.post("/accounts/{account_id}/warming/start")
async def start_warming(
    account_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start WhatsApp warming process"""
    account = db.query(WhatsAppAccount).filter(WhatsAppAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account.is_warming = True
    account.status = "warming"
    db.commit()
    
    # Start warming task in background
    background_tasks.add_task(run_warming_process, account_id, db)
    
    return {"status": "warming_started", "account_id": account_id}


async def run_warming_process(account_id: int, db: Session):
    """Background task for warming WhatsApp account"""
    account = db.query(WhatsAppAccount).filter(WhatsAppAccount.id == account_id).first()
    if not account:
        return
    
    level = account.warming_level or 1
    min_delay, max_delay = get_warming_delays(level)
    msg_limit = get_warming_message_limit(level)
    
    messages_sent = 0
    
    while account.is_warming and messages_sent < msg_limit:
        # Simulate sending warm-up messages
        await asyncio.sleep(randomize_delay(min_delay, max_delay))
        messages_sent += 1
        
        # Update progress
        account.warming_level = min(10, level + (messages_sent // 50))
        db.commit()
    
    account.is_warming = False
    account.status = "connected"
    db.commit()


@app.post("/accounts/{account_id}/recovery/click")
async def trigger_recovery_click(
    account_id: int,
    db: Session = Depends(get_db)
):
    """Trigger auto-click for recovery link"""
    account = db.query(WhatsAppAccount).filter(WhatsAppAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    recovery_link = generate_recovery_link(account.phone_number)
    
    if account.session_id in active_sessions:
        session = active_sessions[account.session_id]
        clicked = await session.click_link(recovery_link)
        
        if clicked:
            return {
                "status": "recovery_initiated",
                "link": recovery_link,
                "clicked": True
            }
    
    return {
        "status": "recovery_pending",
        "link": recovery_link,
        "clicked": False
    }


@app.get("/accounts/{account_id}/status")
async def get_account_status(account_id: int, db: Session = Depends(get_db)):
    """Get WhatsApp account status"""
    account = db.query(WhatsAppAccount).filter(WhatsAppAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return {
        "id": account.id,
        "phone_number": account.phone_number,
        "status": account.status,
        "is_warming": account.is_warming,
        "warming_level": account.warming_level,
        "last_active": account.last_active
    }


if __name__ == "__main__":
    import uvicorn
    from shared.utils import randomize_delay
    uvicorn.run(app, host="0.0.0.0", port=8003)
