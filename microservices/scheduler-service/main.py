"""
Scheduler Service - Task scheduling and queue management
Handles: warming schedules, campaign scheduling, recurring tasks
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import asyncio
import json

from shared.database import get_db
from shared.models import WarmingSchedule, WhatsAppAccount, BlastCampaign
from shared.schemas import WarmingScheduleCreate, WarmingScheduleResponse
from shared.utils import get_warming_delays, get_warming_message_limit
from shared.config import settings

app = FastAPI(title="Scheduler Service", version="1.0.0")

# In-memory task queue (use Redis/Celery in production)
task_queue: Dict[str, dict] = {}


class TaskScheduler:
    """Task scheduler for background jobs"""
    
    def __init__(self):
        self.scheduled_tasks = {}
    
    async def schedule_task(
        self,
        task_id: str,
        task_type: str,
        execute_at: datetime,
        payload: dict
    ):
        """Schedule a task for later execution"""
        self.scheduled_tasks[task_id] = {
            "task_type": task_type,
            "execute_at": execute_at,
            "payload": payload,
            "status": "scheduled"
        }
        
        # Calculate delay
        delay = (execute_at - datetime.now()).total_seconds()
        
        if delay > 0:
            # Schedule async execution
            asyncio.create_task(self._execute_delayed(task_id, delay))
        else:
            # Execute immediately
            asyncio.create_task(self._execute_task(task_id))
        
        return task_id
    
    async def _execute_delayed(self, task_id: str, delay: float):
        """Execute task after delay"""
        await asyncio.sleep(delay)
        await self._execute_task(task_id)
    
    async def _execute_task(self, task_id: str):
        """Execute a scheduled task"""
        if task_id not in self.scheduled_tasks:
            return
        
        task = self.scheduled_tasks[task_id]
        task["status"] = "running"
        
        try:
            if task["task_type"] == "warming":
                await self._execute_warming(task["payload"])
            elif task["task_type"] == "campaign":
                await self._execute_campaign(task["payload"])
            
            task["status"] = "completed"
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
    
    async def _execute_warming(self, payload: dict):
        """Execute warming task"""
        # This would integrate with WhatsApp service
        pass
    
    async def _execute_campaign(self, payload: dict):
        """Execute campaign sending task"""
        # This would integrate with Blast service
        pass


scheduler = TaskScheduler()


@app.post("/warming-schedules", response_model=WarmingScheduleResponse)
async def create_warming_schedule(
    schedule_data: WarmingScheduleCreate,
    db: Session = Depends(get_db)
):
    """Create a warming schedule for a WhatsApp account"""
    db_schedule = WarmingSchedule(
        whatsapp_account_id=schedule_data.whatsapp_account_id,
        day=schedule_data.day,
        messages_per_day=schedule_data.messages_per_day,
        min_delay_seconds=schedule_data.min_delay_seconds,
        max_delay_seconds=schedule_data.max_delay_seconds,
        is_active=schedule_data.is_active
    )
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    
    return db_schedule


@app.get("/warming-schedules/{account_id}")
async def get_warming_schedules(
    account_id: int,
    db: Session = Depends(get_db)
):
    """Get all warming schedules for an account"""
    schedules = db.query(WarmingSchedule).filter(
        WarmingSchedule.whatsapp_account_id == account_id
    ).order_by(WarmingSchedule.day.asc()).all()
    
    return schedules


@app.post("/warming-schedules/auto-generate/{account_id}")
async def auto_generate_warming_schedule(
    account_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Auto-generate a 30-day warming schedule"""
    # Delete existing schedules
    db.query(WarmingSchedule).filter(
        WarmingSchedule.whatsapp_account_id == account_id
    ).delete()
    
    schedules = []
    
    # Generate progressive warming schedule
    for day in range(1, days + 1):
        if day <= 7:
            # Week 1: Very conservative
            messages = 10 + (day * 5)
            min_delay = 300
            max_delay = 600
        elif day <= 14:
            # Week 2: Gradual increase
            messages = 50 + ((day - 7) * 10)
            min_delay = 180
            max_delay = 360
        elif day <= 21:
            # Week 3: Moderate
            messages = 120 + ((day - 14) * 15)
            min_delay = 120
            max_delay = 240
        else:
            # Week 4+: Normal usage
            messages = 200 + ((day - 21) * 10)
            min_delay = 60
            max_delay = 180
        
        schedule = WarmingSchedule(
            whatsapp_account_id=account_id,
            day=day,
            messages_per_day=min(messages, 200),
            min_delay_seconds=min_delay,
            max_delay_seconds=max_delay,
            is_active=True
        )
        
        db.add(schedule)
        schedules.append(schedule)
    
    db.commit()
    
    return {
        "account_id": account_id,
        "days": days,
        "schedules_created": len(schedules)
    }


@app.post("/tasks/schedule")
async def schedule_task(
    task_type: str,
    execute_at: datetime,
    payload: dict,
    db: Session = Depends(get_db)
):
    """Schedule a custom task"""
    task_id = f"{task_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    scheduled_id = await scheduler.schedule_task(
        task_id=task_id,
        task_type=task_type,
        execute_at=execute_at,
        payload=payload
    )
    
    task_queue[task_id] = {
        "task_type": task_type,
        "execute_at": execute_at,
        "payload": payload,
        "status": "scheduled"
    }
    
    return {
        "task_id": scheduled_id,
        "status": "scheduled",
        "execute_at": execute_at
    }


@app.get("/tasks")
async def list_tasks(status: Optional[str] = None):
    """List all scheduled tasks"""
    tasks = task_queue
    
    if status:
        tasks = {k: v for k, v in task_queue.items() if v.get("status") == status}
    
    return {
        "count": len(tasks),
        "tasks": tasks
    }


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task details"""
    if task_id not in task_queue:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_queue[task_id]


@app.delete("/tasks/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a scheduled task"""
    if task_id not in task_queue:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_queue[task_id]["status"] == "running":
        raise HTTPException(status_code=400, detail="Cannot cancel running task")
    
    del task_queue[task_id]
    
    if task_id in scheduler.scheduled_tasks:
        del scheduler.scheduled_tasks[task_id]
    
    return {"status": "cancelled", "task_id": task_id}


@app.post("/campaigns/{campaign_id}/schedule")
async def schedule_campaign(
    campaign_id: int,
    scheduled_at: datetime,
    db: Session = Depends(get_db)
):
    """Schedule a campaign for later execution"""
    campaign = db.query(BlastCampaign).filter(BlastCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Update campaign
    campaign.scheduled_at = scheduled_at
    campaign.status = "scheduled"
    db.commit()
    
    # Schedule task
    task_id = f"campaign_{campaign_id}"
    await scheduler.schedule_task(
        task_id=task_id,
        task_type="campaign",
        execute_at=scheduled_at,
        payload={"campaign_id": campaign_id}
    )
    
    task_queue[task_id] = {
        "task_type": "campaign",
        "execute_at": scheduled_at,
        "payload": {"campaign_id": campaign_id},
        "status": "scheduled"
    }
    
    return {
        "campaign_id": campaign_id,
        "scheduled_at": scheduled_at,
        "task_id": task_id
    }


@app.get("/queue/stats")
async def get_queue_stats():
    """Get task queue statistics"""
    stats = {
        "total": len(task_queue),
        "scheduled": sum(1 for t in task_queue.values() if t.get("status") == "scheduled"),
        "running": sum(1 for t in task_queue.values() if t.get("status") == "running"),
        "completed": sum(1 for t in task_queue.values() if t.get("status") == "completed"),
        "failed": sum(1 for t in task_queue.values() if t.get("status") == "failed")
    }
    
    return stats


@app.post("/cron/warming-check")
async def check_warming_schedules(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Check and activate warming schedules (run periodically)"""
    # Get accounts that need warming today
    today = datetime.now().weekday() + 1  # 1-7 for Mon-Sun
    
    accounts_to_warm = db.query(WhatsAppAccount).filter(
        WhatsAppAccount.is_warming == True
    ).all()
    
    activated = []
    for account in accounts_to_warm:
        schedule = db.query(WarmingSchedule).filter(
            WarmingSchedule.whatsapp_account_id == account.id,
            WarmingSchedule.day == today,
            WarmingSchedule.is_active == True
        ).first()
        
        if schedule:
            activated.append(account.id)
            # Start warming process
            background_tasks.add_task(start_warming_process, account.id, schedule, db)
    
    return {
        "status": "checked",
        "accounts_activated": activated,
        "count": len(activated)
    }


async def start_warming_process(account_id: int, schedule: WarmingSchedule, db: Session):
    """Background task to start warming process"""
    # This would integrate with WhatsApp service
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
