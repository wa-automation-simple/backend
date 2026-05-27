"""AI Auto-Reply API Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from ai.api.deps import get_db, get_ai_service
from ai.services.reply_service import AIReplyService
from ai.schemas.serializers import (
    AIReplyCreate, 
    AIReplyUpdate, 
    AIReplyResponse,
    TokenUsageResponse
)

router = APIRouter(prefix="/api/v1", tags=["ai-replies"])


@router.post("/replies", response_model=AIReplyResponse, status_code=status.HTTP_201_CREATED)
def create_ai_reply(
    data: AIReplyCreate,
    current_user_id: int = 1,  # TODO: Get from JWT token
    service: AIReplyService = Depends(get_ai_service)
):
    """Create new AI auto-reply configuration"""
    return service.create_reply(user_id=current_user_id, data=data)


@router.get("/replies", response_model=List[AIReplyResponse])
def get_user_replies(
    current_user_id: int = 1,  # TODO: Get from JWT token
    service: AIReplyService = Depends(get_ai_service)
):
    """Get all AI replies for current user"""
    return service.get_user_replies(user_id=current_user_id)


@router.get("/replies/{reply_id}", response_model=AIReplyResponse)
def get_ai_reply(
    reply_id: int,
    service: AIReplyService = Depends(get_ai_service)
):
    """Get specific AI reply by ID"""
    reply = service.get_reply(reply_id)
    if not reply:
        raise HTTPException(status_code=404, detail="AI reply not found")
    return reply


@router.put("/replies/{reply_id}", response_model=AIReplyResponse)
def update_ai_reply(
    reply_id: int,
    data: AIReplyUpdate,
    service: AIReplyService = Depends(get_ai_service)
):
    """Update AI reply configuration"""
    reply = service.update_reply(reply_id, data)
    if not reply:
        raise HTTPException(status_code=404, detail="AI reply not found")
    return reply


@router.delete("/replies/{reply_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ai_reply(
    reply_id: int,
    service: AIReplyService = Depends(get_ai_service)
):
    """Delete AI reply configuration"""
    success = service.delete_reply(reply_id)
    if not success:
        raise HTTPException(status_code=404, detail="AI reply not found")


@router.post("/replies/{reply_id}/toggle", response_model=AIReplyResponse)
def toggle_ai_reply(
    reply_id: int,
    service: AIReplyService = Depends(get_ai_service)
):
    """Toggle AI reply enable/disable status"""
    reply = service.toggle_reply(reply_id)
    if not reply:
        raise HTTPException(status_code=404, detail="AI reply not found")
    return reply


@router.get("/replies/account/{whatsapp_account_id}", response_model=AIReplyResponse)
def get_whatsapp_reply(
    whatsapp_account_id: int,
    service: AIReplyService = Depends(get_ai_service)
):
    """Get AI reply configuration for specific WhatsApp account"""
    reply = service.get_whatsapp_reply(whatsapp_account_id)
    if not reply:
        raise HTTPException(status_code=404, detail="AI reply not found for this account")
    return reply
