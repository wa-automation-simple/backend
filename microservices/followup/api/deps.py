"""Dependency injection for Followup service"""
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Generator
from followup.core.database import SessionLocal
from followup.services.followup_service import FollowUpService


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_followup_service(db: Session = Depends(get_db)) -> FollowUpService:
    return FollowUpService(db)
