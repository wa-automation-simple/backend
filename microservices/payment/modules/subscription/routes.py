"""Subscription Routes"""
from fastapi import APIRouter, Depends, HTTPException
from payment.modules.subscription.service import SubscriptionService
from payment.modules.subscription.schemas import SubscriptionCreate, SubscriptionResponse

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


def get_subscription_service():
    """Dependency to get subscription service"""
    from sqlalchemy.orm import Session
    from payment.core.database import SessionLocal
    db = SessionLocal()
    try:
        return SubscriptionService(db)
    finally:
        db.close()


@router.post("", response_model=SubscriptionResponse)
def create_subscription(
    data: SubscriptionCreate,
    current_user_id: int = 1,  # TODO: Get from JWT token
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Create monthly subscription"""
    return service.create_subscription(current_user_id, data)


@router.post("/{subscription_id}/cancel")
def cancel_subscription(
    subscription_id: int,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """Cancel subscription"""
    return service.cancel_subscription(subscription_id)
