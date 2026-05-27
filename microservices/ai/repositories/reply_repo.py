"""Repository for AI Reply data access"""
from sqlalchemy.orm import Session
from typing import List, Optional
from ai.models.ai_reply import AIReply
from datetime import datetime


class AIReplyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, **kwargs) -> AIReply:
        """Create a new AI reply configuration"""
        ai_reply = AIReply(user_id=user_id, **kwargs)
        self.db.add(ai_reply)
        self.db.commit()
        self.db.refresh(ai_reply)
        return ai_reply

    def get_by_id(self, reply_id: int) -> Optional[AIReply]:
        """Get AI reply by ID"""
        return self.db.query(AIReply).filter(AIReply.id == reply_id).first()

    def get_by_user(self, user_id: int) -> List[AIReply]:
        """Get all AI replies for a user"""
        return self.db.query(AIReply).filter(AIReply.user_id == user_id).all()

    def get_by_whatsapp_account(self, whatsapp_account_id: int) -> Optional[AIReply]:
        """Get AI reply for specific WhatsApp account"""
        return self.db.query(AIReply).filter(
            AIReply.whatsapp_account_id == whatsapp_account_id
        ).first()

    def update(self, reply_id: int, **kwargs) -> Optional[AIReply]:
        """Update AI reply configuration"""
        ai_reply = self.get_by_id(reply_id)
        if not ai_reply:
            return None
        
        for key, value in kwargs.items():
            if hasattr(ai_reply, key):
                setattr(ai_reply, key, value)
        
        ai_reply.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(ai_reply)
        return ai_reply

    def delete(self, reply_id: int) -> bool:
        """Delete AI reply configuration"""
        ai_reply = self.get_by_id(reply_id)
        if not ai_reply:
            return False
        
        self.db.delete(ai_reply)
        self.db.commit()
        return True

    def increment_tokens_used(self, reply_id: int, tokens: int) -> Optional[AIReply]:
        """Increment token usage counter"""
        ai_reply = self.get_by_id(reply_id)
        if not ai_reply:
            return None
        
        ai_reply.tokens_used += tokens
        ai_reply.last_used_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(ai_reply)
        return ai_reply

    def toggle_enable(self, reply_id: int) -> Optional[AIReply]:
        """Toggle AI enable/disable status"""
        ai_reply = self.get_by_id(reply_id)
        if not ai_reply:
            return None
        
        ai_reply.enable_ai = not ai_reply.enable_ai
        ai_reply.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(ai_reply)
        return ai_reply
