"""Subscription Service"""
from typing import Optional
from sqlalchemy.orm import Session
from payment.models.subscription.repository import SubscriptionRepository
from payment.models.wallet.service import WalletService
from payment.models.subscription.schemas import SubscriptionCreate
from datetime import datetime, timedelta


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SubscriptionRepository(db)
        self.wallet_service = WalletService(db)

    def create_subscription(self, user_id: int, data: SubscriptionCreate):
        """Create monthly subscription"""
        wallet = self.wallet_service.get_or_create_wallet(user_id)
        
        subscription = self.repo.create_subscription(
            user_id=user_id,
            wallet_id=wallet.id,
            plan_name=data.plan_name,
            tokens_per_month=data.tokens_per_month,
            monthly_price=data.monthly_price,
            billing_cycle_start=datetime.utcnow(),
            next_billing_date=datetime.utcnow() + timedelta(days=30),
            is_active=True
        )

        # Add initial tokens
        self.wallet_service.update_balance(wallet.id, data.tokens_per_month)

        return subscription

    def cancel_subscription(self, subscription_id: int):
        """Cancel subscription"""
        return self.repo.cancel_subscription(subscription_id)

    def get_user_subscription(self, user_id: int) -> Optional:
        """Get active subscription for user"""
        return self.repo.get_user_subscription(user_id)
