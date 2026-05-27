"""Service layer for Followup business logic"""
from typing import List, Optional
from sqlalchemy.orm import Session
from followup.repositories.followup_repo import FollowUpRepository
from followup.schemas.serializers import LeadCreate, LeadUpdate, InteractionLogCreate, FollowUpSequenceCreate
from datetime import datetime, timedelta


class FollowUpService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FollowUpRepository(db)

    def create_lead(self, user_id: int, whatsapp_account_id: int, data: LeadCreate):
        """Create new lead"""
        return self.repo.create_lead(
            user_id=user_id,
            whatsapp_account_id=whatsapp_account_id,
            phone_number=data.phone_number,
            name=data.name,
            tags=','.join(data.tags) if data.tags else None,
            source=data.source,
            campaign_id=data.campaign_id,
            priority=data.priority,
            notes=data.notes,
            next_followup_date=data.next_followup_date or (datetime.utcnow() + timedelta(days=1)),
            max_followups=data.max_followups
        )

    def get_leads(self, user_id: int, status: str = None):
        """Get leads for user"""
        return self.repo.get_leads_by_user(user_id, status)

    def get_lead(self, lead_id: int):
        """Get lead by ID"""
        return self.repo.get_lead(lead_id)

    def update_lead(self, lead_id: int, data: LeadUpdate):
        """Update lead"""
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        
        # Convert tags list to comma-separated string
        if 'tags' in update_data and update_data['tags']:
            update_data['tags'] = ','.join(update_data['tags'])
        
        return self.repo.update_lead(lead_id, **update_data)

    def log_interaction(self, user_id: int, whatsapp_account_id: int, data: InteractionLogCreate):
        """Log interaction with lead"""
        interaction = self.repo.create_interaction(
            lead_id=data.lead_id,
            user_id=user_id,
            whatsapp_account_id=whatsapp_account_id,
            interaction_type=data.interaction_type,
            content=data.content,
            media_url=data.media_url,
            is_outbound=data.is_outbound,
            followup_sequence_id=data.followup_sequence_id,
            sequence_step=data.sequence_step
        )

        # Update lead's last interaction
        lead = self.repo.get_lead(data.lead_id)
        if lead:
            self.repo.update_lead(
                data.lead_id,
                last_interaction=datetime.utcnow(),
                status="in_progress" if lead.status == "pending" else lead.status
            )

        return interaction

    def perform_followup(self, lead_id: int, interval_days: int = 3):
        """Perform follow-up and schedule next one"""
        lead = self.repo.get_lead(lead_id)
        if not lead:
            return None

        next_date = datetime.utcnow() + timedelta(days=interval_days)
        return self.repo.increment_followup_count(lead_id, next_date)

    def get_due_followups(self, user_id: int):
        """Get leads due for follow-up"""
        return self.repo.get_leads_due_for_followup(user_id)

    def create_sequence(self, user_id: int, data: FollowUpSequenceCreate):
        """Create follow-up sequence"""
        return self.repo.create_sequence(
            user_id=user_id,
            name=data.name,
            description=data.description,
            interval_days=data.interval_days,
            messages=data.messages
        )

    def get_sequences(self, user_id: int):
        """Get sequences for user"""
        return self.repo.get_sequences_by_user(user_id)

    def get_interactions(self, lead_id: int):
        """Get interactions for lead"""
        return self.repo.get_interactions_by_lead(lead_id)
