"""Dependency injection for Payment service"""
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Generator
from payment.core.database import SessionLocal
from payment.services.payment_service import PaymentService


def get_db() -> Generator:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    """Get payment service instance"""
    return PaymentService(db)
