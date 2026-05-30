"""API routes for ChatbotNode module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from modules.chatbot_node.schemas import ChatbotNodeCreate, ChatbotNodeUpdate, ChatbotNodeResponse
from modules.chatbot_node.service import ChatbotNodeService

router = APIRouter(prefix="/chatbot_nodes", tags=["ChatbotNodes"])


@router.post("", response_model=ChatbotNodeResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_data: ChatbotNodeCreate, db: Session = Depends(get_db)):
    """Create a new chatbot_node."""
    service = ChatbotNodeService(db)
    return service.create_item(item_data=item_data)


@router.get("", response_model=List[ChatbotNodeResponse])
def list_items(db: Session = Depends(get_db)):
    """List all items."""
    service = ChatbotNodeService(db)
    return service.list_items()


@router.get("/{item_id}", response_model=ChatbotNodeResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get chatbot_node by ID."""
    service = ChatbotNodeService(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ChatbotNode not found")
    return item


@router.put("/{item_id}", response_model=ChatbotNodeResponse)
def update_item(item_id: int, item_data: ChatbotNodeUpdate, db: Session = Depends(get_db)):
    """Update chatbot_node."""
    service = ChatbotNodeService(db)
    item = service.update_item(item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="ChatbotNode not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a chatbot_node."""
    service = ChatbotNodeService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="ChatbotNode not found")
