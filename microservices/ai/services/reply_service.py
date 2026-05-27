"""Service layer for AI auto-reply business logic"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ai.repositories.reply_repo import AIReplyRepository
from ai.schemas.serializers import AIReplyCreate, AIReplyUpdate
import re


class AIReplyService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AIReplyRepository(db)

    def create_reply(self, user_id: int, data: AIReplyCreate) -> Any:
        """Create new AI auto-reply configuration"""
        return self.repo.create(
            user_id=user_id,
            whatsapp_account_id=data.whatsapp_account_id,
            trigger_type=data.trigger_type,
            trigger_keywords=data.trigger_keywords,
            trigger_pattern=data.trigger_pattern,
            system_prompt=data.system_prompt,
            max_tokens=data.max_tokens,
            temperature=data.temperature,
            enable_ai=data.enable_ai,
            fallback_message=data.fallback_message
        )

    def get_reply(self, reply_id: int) -> Optional[Any]:
        """Get AI reply by ID"""
        return self.repo.get_by_id(reply_id)

    def get_user_replies(self, user_id: int) -> List[Any]:
        """Get all AI replies for a user"""
        return self.repo.get_by_user(user_id)

    def get_whatsapp_reply(self, whatsapp_account_id: int) -> Optional[Any]:
        """Get AI reply for specific WhatsApp account"""
        return self.repo.get_by_whatsapp_account(whatsapp_account_id)

    def update_reply(self, reply_id: int, data: AIReplyUpdate) -> Optional[Any]:
        """Update AI reply configuration"""
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        return self.repo.update(reply_id, **update_data)

    def delete_reply(self, reply_id: int) -> bool:
        """Delete AI reply configuration"""
        return self.repo.delete(reply_id)

    def toggle_reply(self, reply_id: int) -> Optional[Any]:
        """Toggle AI reply enable/disable"""
        return self.repo.toggle_enable(reply_id)

    def should_trigger_ai(self, message: str, reply_config: Any) -> bool:
        """Check if incoming message should trigger AI response"""
        if not reply_config or not reply_config.enable_ai:
            return False

        if reply_config.trigger_type == "always":
            return True

        if reply_config.trigger_type == "keyword":
            message_lower = message.lower()
            for keyword in reply_config.trigger_keywords:
                if keyword.lower() in message_lower:
                    return True
            return False

        if reply_config.trigger_type == "pattern" and reply_config.trigger_pattern:
            try:
                if re.search(reply_config.trigger_pattern, message):
                    return True
            except re.error:
                pass
            return False

        return False

    def generate_response_prompt(self, message: str, reply_config: Any, history: List[Dict]) -> Dict[str, Any]:
        """Generate prompt configuration for AI model"""
        messages = [
            {"role": "system", "content": reply_config.system_prompt}
        ]
        
        # Add conversation history
        messages.extend(history[-10:])  # Last 10 messages
        
        # Add current message
        messages.append({"role": "user", "content": message})

        return {
            "messages": messages,
            "max_tokens": reply_config.max_tokens,
            "temperature": reply_config.temperature
        }
