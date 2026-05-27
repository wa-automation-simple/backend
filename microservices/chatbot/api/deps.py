"""
Dependency injection for Chatbot Service
"""
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from core.database import get_db
from config import get_chatbot_settings

settings = get_chatbot_settings()


def verify_static_token(x_api_key: str = Header(..., alias="X-API-Key")):
    """
    Verify static token for /chat endpoint
    Different from JWT access_token used in other services
    """
    if not x_api_key.startswith(settings.CHAT_STATIC_TOKEN_PREFIX):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format. Must start with 'chat_'",
            headers={"WWW-Authenticate": "API-Key"},
        )
    
    # In production, validate against database
    # For now, check against configured default token
    if x_api_key != settings.DEFAULT_CHAT_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API-Key"},
        )
    
    return x_api_key


async def get_chatbot_by_token(token: str, db: Session = Depends(get_db)):
    """Get chatbot by static token"""
    from models.chatbot import Chatbot
    
    chatbot = db.query(Chatbot).filter(Chatbot.static_token == token).first()
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatbot not found"
        )
    
    if not chatbot.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chatbot is deactivated"
        )
    
    return chatbot
