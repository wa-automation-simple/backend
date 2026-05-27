"""API routes for ChatbotAgent module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from chatbot.core.database import get_db
from chatbot.modules.chatbot_agent.schemas import ChatbotAgentCreate, ChatbotAgentUpdate, ChatbotAgentResponse
from chatbot.modules.chatbot_agent.service import ChatbotAgentService

router = APIRouter(prefix="/chatbot_agents", tags=["ChatbotAgents"])


@router.post("", response_model=ChatbotAgentResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_data: ChatbotAgentCreate, db: Session = Depends(get_db)):
    """Create a new chatbot_agent."""
    service = ChatbotAgentService(db)
    return service.create_item(item_data=item_data)


@router.get("", response_model=List[ChatbotAgentResponse])
def list_items(db: Session = Depends(get_db)):
    """List all items."""
    service = ChatbotAgentService(db)
    return service.list_items()


@router.get("/{item_id}", response_model=ChatbotAgentResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get chatbot_agent by ID."""
    service = ChatbotAgentService(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ChatbotAgent not found")
    return item


@router.put("/{item_id}", response_model=ChatbotAgentResponse)
def update_item(item_id: int, item_data: ChatbotAgentUpdate, db: Session = Depends(get_db)):
    """Update chatbot_agent."""
    service = ChatbotAgentService(db)
    item = service.update_item(item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="ChatbotAgent not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a chatbot_agent."""
    service = ChatbotAgentService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="ChatbotAgent not found")
