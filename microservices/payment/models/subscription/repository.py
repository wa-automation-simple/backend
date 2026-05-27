"""Subscription Repository"""
from sqlalchemy.orm import Session
from typing import List, Optional
from payment.models.subscription.subscription import Subscription
from datetime import datetime


class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_subscription(self, subscription_id: int) -> Optional[Subscription]:
        """Get subscription by ID"""
        return self.db.query(Subscription).filter(Subscription.id == subscription_id).first()

    def get_user_subscription(self, user_id: int) -> Optional[Subscription]:
        """Get active subscription for user"""
        return self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        ).first()

    def create_subscription(self, **kwargs) -> Subscription:
        """Create new subscription"""
        subscription = Subscription(**kwargs)
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def cancel_subscription(self, subscription_id: int) -> Optional[Subscription]:
        """Cancel subscription at period end"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            return None
        
        subscription.cancel_at_period_end = True
        subscription.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
