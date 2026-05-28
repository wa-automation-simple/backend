"""API routes for Chatbot module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
import secrets

from chatbot.core.database import get_db
from chatbot.modules.chatbot.schemas import ChatbotCreate, ChatbotUpdate, ChatbotResponse
from chatbot.modules.chatbot.service import ChatbotService
from chatbot.middleware.auth import get_current_user

router = APIRouter(prefix="/chatbots", tags=["Chatbots"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    chatbot_id: UUID
    message: str
    conversation_id: Optional[UUID] = None
    user_id: Optional[str] = None
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    conversation_id: UUID
    messages: list


@router.post("", response_model=ChatbotResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ChatbotCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new chatbot with agents, tools, and nodes in one request."""
    service = ChatbotService(db)
    # Extract user_id from authenticated user (should be UUID now)
    user_id = current_user.get('user_id') or current_user.get('id')
    return await service.create_item(item_data=item_data, user_id=user_id)


@router.get("", response_model=List[ChatbotResponse])
async def list_items(user_id: Optional[UUID] = None, db: AsyncSession = Depends(get_db)):
    """List all items, optionally filtered by user_id."""
    service = ChatbotService(db)
    return await service.list_items(user_id=user_id)


@router.get("/{item_id}", response_model=ChatbotResponse)
async def get_item(item_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get chatbot by ID."""
    service = ChatbotService(db)
    item = await service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return item


@router.put("/{item_id}", response_model=ChatbotResponse)
async def update_item(item_id: UUID, item_data: ChatbotUpdate, db: AsyncSession = Depends(get_db)):
    """Update chatbot."""
    service = ChatbotService(db)
    item = await service.update_item(item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a chatbot."""
    service = ChatbotService(db)
    success = await service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chatbot not found")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Send a message to a chatbot using static token authentication."""
    service = ChatbotService(db)
    
    result = await service.process_message(
        chatbot_id=request.chatbot_id,
        user_message=request.message,
        conversation_id=request.conversation_id,
        user_id=request.user_id,
        context=request.context
    )
    
    return ChatResponse(**result)


@router.get("/{item_id}/token/regenerate", response_model=ChatbotResponse)
async def regenerate_token(item_id: UUID, db: AsyncSession = Depends(get_db)):
    """Regenerate static token for a chatbot."""
    service = ChatbotService(db)
    new_token = await service.regenerate_static_token(item_id)
    if not new_token:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return await service.get_item(item_id)


@router.post("/chat-by-token/{static_token}", response_model=ChatResponse)
async def chat_by_token(static_token: str, request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Send a message to a chatbot using static token in URL path."""
    service = ChatbotService(db)
    
    # Find chatbot by static token
    chatbot = await service.get_by_static_token(static_token)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    if not chatbot.is_active:
        raise HTTPException(status_code=403, detail="Chatbot is not active")
    
    result = await service.process_message(
        chatbot_id=chatbot.id,
        user_message=request.message,
        conversation_id=request.conversation_id,
        user_id=request.user_id,
        context=request.context
    )
    
    return ChatResponse(**result)
