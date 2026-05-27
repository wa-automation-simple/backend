"""Repository for Followup data access"""
from sqlalchemy.orm import Session
from typing import List, Optional
from followup.models.follow_up import Lead, InteractionLog, FollowUpSequence, FollowUpStatus
from datetime import datetime, timedelta


class FollowUpRepository:
    def __init__(self, db: Session):
        self.db = db

    # Lead Operations
    def create_lead(self, **kwargs) -> Lead:
        """Create new lead"""
        lead = Lead(**kwargs)
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def get_lead(self, lead_id: int) -> Optional[Lead]:
        """Get lead by ID"""
        return self.db.query(Lead).filter(Lead.id == lead_id).first()

    def get_leads_by_user(self, user_id: int, status: str = None, limit: int = 100) -> List[Lead]:
        """Get leads for user with optional status filter"""
        query = self.db.query(Lead).filter(Lead.user_id == user_id)
        if status:
            query = query.filter(Lead.status == status)
        return query.order_by(Lead.priority.desc(), Lead.created_at.desc()).limit(limit).all()

    def get_leads_due_for_followup(self, user_id: int) -> List[Lead]:
        """Get leads that are due for follow-up"""
        now = datetime.utcnow()
        return self.db.query(Lead).filter(
            Lead.user_id == user_id,
            Lead.status.in_([FollowUpStatus.PENDING, FollowUpStatus.IN_PROGRESS]),
            Lead.next_followup_date <= now,
            Lead.followup_count < Lead.max_followups
        ).all()

    def update_lead(self, lead_id: int, **kwargs) -> Optional[Lead]:
        """Update lead"""
        lead = self.get_lead(lead_id)
        if not lead:
            return None
        
        for key, value in kwargs.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        
        lead.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def increment_followup_count(self, lead_id: int, next_date: datetime) -> Optional[Lead]:
        """Increment follow-up count and set next date"""
        lead = self.get_lead(lead_id)
        if not lead:
            return None
        
        lead.followup_count += 1
        lead.next_followup_date = next_date
        lead.last_interaction = datetime.utcnow()
        
        if lead.followup_count >= lead.max_followups:
            lead.status = FollowUpStatus.COMPLETED
        
        self.db.commit()
        self.db.refresh(lead)
        return lead

    # Interaction Log Operations
    def create_interaction(self, **kwargs) -> InteractionLog:
        """Create interaction log"""
        interaction = InteractionLog(**kwargs)
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def get_interactions_by_lead(self, lead_id: int, limit: int = 50) -> List[InteractionLog]:
        """Get interactions for a lead"""
        return self.db.query(InteractionLog).filter(
            InteractionLog.lead_id == lead_id
        ).order_by(InteractionLog.created_at.desc()).limit(limit).all()

    # Follow-up Sequence Operations
    def create_sequence(self, **kwargs) -> FollowUpSequence:
        """Create follow-up sequence"""
        import json
        messages = kwargs.pop('messages', [])
        sequence = FollowUpSequence(
            **kwargs,
            messages=json.dumps(messages),
            total_steps=len(messages)
        )
        self.db.add(sequence)
        self.db.commit()
        self.db.refresh(sequence)
        return sequence

    def get_sequences_by_user(self, user_id: int) -> List[FollowUpSequence]:
        """Get sequences for user"""
        return self.db.query(FollowUpSequence).filter(
            FollowUpSequence.user_id == user_id,
            FollowUpSequence.is_active == True
        ).all()

    def get_sequence(self, sequence_id: int) -> Optional[FollowUpSequence]:
        """Get sequence by ID"""
        return self.db.query(FollowUpSequence).filter(FollowUpSequence.id == sequence_id).first()
