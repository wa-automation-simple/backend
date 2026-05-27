"""API routes for ChatbotTool module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from chatbot.core.database import get_db
from chatbot.modules.chatbot_tool.schemas import ChatbotToolCreate, ChatbotToolUpdate, ChatbotToolResponse
from chatbot.modules.chatbot_tool.service import ChatbotToolService

router = APIRouter(prefix="/chatbot_tools", tags=["ChatbotTools"])


@router.post("", response_model=ChatbotToolResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_data: ChatbotToolCreate, db: Session = Depends(get_db)):
    """Create a new chatbot_tool."""
    service = ChatbotToolService(db)
    return service.create_item(item_data=item_data)


@router.get("", response_model=List[ChatbotToolResponse])
def list_items(db: Session = Depends(get_db)):
    """List all items."""
    service = ChatbotToolService(db)
    return service.list_items()


@router.get("/{item_id}", response_model=ChatbotToolResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get chatbot_tool by ID."""
    service = ChatbotToolService(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ChatbotTool not found")
    return item


@router.put("/{item_id}", response_model=ChatbotToolResponse)
def update_item(item_id: int, item_data: ChatbotToolUpdate, db: Session = Depends(get_db)):
    """Update chatbot_tool."""
    service = ChatbotToolService(db)
    item = service.update_item(item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="ChatbotTool not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a chatbot_tool."""
    service = ChatbotToolService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="ChatbotTool not found")
