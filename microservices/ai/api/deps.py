"""Dependency injection for AI service"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Generator
from ai.core.database import SessionLocal
from ai.services.reply_service import AIReplyService


def get_db() -> Generator:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_ai_service(db: Session = Depends(get_db)) -> AIReplyService:
    """Get AI reply service instance"""
    return AIReplyService(db)
