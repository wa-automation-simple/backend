"""API routes for ChatbotState module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from chatbot.core.database import get_db
from chatbot.modules.chatbot_state.schemas import ChatbotStateCreate, ChatbotStateUpdate, ChatbotStateResponse
from chatbot.modules.chatbot_state.service import ChatbotStateService

router = APIRouter(prefix="/chatbot_states", tags=["ChatbotStates"])


@router.post("", response_model=ChatbotStateResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_data: ChatbotStateCreate, db: Session = Depends(get_db)):
    """Create a new chatbot_state."""
    service = ChatbotStateService(db)
    return service.create_item(item_data=item_data)


@router.get("", response_model=List[ChatbotStateResponse])
def list_items(db: Session = Depends(get_db)):
    """List all items."""
    service = ChatbotStateService(db)
    return service.list_items()


@router.get("/{item_id}", response_model=ChatbotStateResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get chatbot_state by ID."""
    service = ChatbotStateService(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ChatbotState not found")
    return item


@router.put("/{item_id}", response_model=ChatbotStateResponse)
def update_item(item_id: int, item_data: ChatbotStateUpdate, db: Session = Depends(get_db)):
    """Update chatbot_state."""
    service = ChatbotStateService(db)
    item = service.update_item(item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="ChatbotState not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a chatbot_state."""
    service = ChatbotStateService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="ChatbotState not found")
