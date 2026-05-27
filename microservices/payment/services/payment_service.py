"""Service layer for Payment business logic"""
from typing import List, Optional
from sqlalchemy.orm import Session
from payment.repositories.payment_repo import PaymentRepository
from payment.schemas.serializers import TokenTopup, PaymentCreate, SubscriptionCreate
from payment.config import settings


class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PaymentRepository(db)

    def get_or_create_wallet(self, user_id: int):
        """Get or create token wallet for user"""
        wallet = self.repo.get_wallet_by_user(user_id)
        if not wallet:
            wallet = self.repo.create_wallet(user_id)
        return wallet

    def get_balance(self, user_id: int):
        """Get user token balance"""
        wallet = self.get_or_create_wallet(user_id)
        return {
            "user_id": user_id,
            "balance": wallet.balance,
            "reserved_tokens": wallet.reserved_tokens,
            "available_tokens": wallet.balance - wallet.reserved_tokens,
            "price_per_token": wallet.price_per_token,
            "estimated_value_usd": wallet.balance * wallet.price_per_token
        }

    def get_packages(self):
        """Get all available token packages"""
        return self.repo.get_packages()

    def purchase_tokens(self, user_id: int, data: TokenTopup):
        """Purchase tokens (create pending transaction)"""
        wallet = self.get_or_create_wallet(user_id)
        
        if data.package_id:
            package = self.repo.get_package(data.package_id)
            if not package:
                raise ValueError("Package not found")
            
            tokens = package.total_tokens
            amount = package.sell_price
            package_name = package.name
            bonus = package.bonus_tokens
        else:
            tokens = data.custom_amount
            amount = tokens * settings.SELL_TOKEN_PRICE
            package_name = "Custom Top-up"
            bonus = 0

        # Create pending transaction
        transaction = self.repo.create_transaction(
            user_id=user_id,
            wallet_id=wallet.id,
            transaction_type="purchase",
            tokens_amount=tokens,
            unit_price=settings.SELL_TOKEN_PRICE,
            total_amount=amount,
            payment_method=data.payment_method,
            package_name=package_name,
            bonus_tokens=bonus,
            status="pending",
            description=f"Purchase {tokens} tokens ({package_name})"
        )

        return {
            "transaction_id": transaction.id,
            "tokens": tokens,
            "amount": amount,
            "payment_url": f"/payment/process/{transaction.id}"
        }

    def complete_payment(self, transaction_id: int, payment_id: str):
        """Complete payment and add tokens to wallet"""
        transaction = self.repo.get_transaction(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")

        # Update transaction
        transaction = self.repo.update_transaction_status(transaction_id, "completed")
        transaction.payment_id = payment_id
        self.db.commit()

        # Add tokens to wallet
        total_tokens = transaction.tokens_amount + transaction.bonus_tokens
        self.repo.update_balance(transaction.wallet_id, total_tokens)

        return transaction

    def get_transactions(self, user_id: int):
        """Get user transaction history"""
        return self.repo.get_user_transactions(user_id)

    def deduct_tokens(self, user_id: int, tokens: int, description: str = None, ai_reply_id: int = None):
        """Deduct tokens from wallet (for AI usage)"""
        wallet = self.get_or_create_wallet(user_id)
        
        if wallet.balance < tokens:
            raise ValueError("Insufficient token balance")

        # Deduct from wallet
        self.repo.update_balance(wallet.id, -tokens)

        # Create transaction record
        transaction = self.repo.create_transaction(
            user_id=user_id,
            wallet_id=wallet.id,
            transaction_type="usage",
            tokens_amount=tokens,
            unit_price=wallet.price_per_token,
            total_amount=tokens * wallet.price_per_token,
            status="completed",
            description=description or "AI token usage",
            ai_reply_id=ai_reply_id,
            tokens_used_for_ai=tokens,
            processed_at=None
        )

        return transaction

    def create_subscription(self, user_id: int, data: SubscriptionCreate):
        """Create monthly subscription"""
        from datetime import datetime, timedelta
        
        wallet = self.get_or_create_wallet(user_id)
        
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
        self.repo.update_balance(wallet.id, data.tokens_per_month)

        return subscription

    def cancel_subscription(self, subscription_id: int):
        """Cancel subscription"""
        return self.repo.cancel_subscription(subscription_id)
