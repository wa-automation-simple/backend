"""Repository for Payment data access"""
from sqlalchemy.orm import Session
from typing import List, Optional
from payment.models.payment import TokenWallet, TokenTransaction, TokenPackage, Subscription, PaymentStatus
from datetime import datetime


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    # Token Wallet Operations
    def get_wallet_by_user(self, user_id: int) -> Optional[TokenWallet]:
        """Get token wallet by user ID"""
        return self.db.query(TokenWallet).filter(TokenWallet.user_id == user_id).first()

    def create_wallet(self, user_id: int) -> TokenWallet:
        """Create new token wallet for user"""
        wallet = TokenWallet(user_id=user_id)
        self.db.add(wallet)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def update_balance(self, wallet_id: int, tokens: int) -> Optional[TokenWallet]:
        """Update wallet balance (positive for add, negative for deduct)"""
        wallet = self.db.query(TokenWallet).filter(TokenWallet.id == wallet_id).first()
        if not wallet:
            return None
        
        wallet.balance += tokens
        wallet.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    # Token Transaction Operations
    def create_transaction(self, **kwargs) -> TokenTransaction:
        """Create new token transaction"""
        transaction = TokenTransaction(**kwargs)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get_transaction(self, transaction_id: int) -> Optional[TokenTransaction]:
        """Get transaction by ID"""
        return self.db.query(TokenTransaction).filter(TokenTransaction.id == transaction_id).first()

    def get_user_transactions(self, user_id: int, limit: int = 50) -> List[TokenTransaction]:
        """Get transactions for user"""
        return self.db.query(TokenTransaction).filter(
            TokenTransaction.user_id == user_id
        ).order_by(TokenTransaction.created_at.desc()).limit(limit).all()

    def update_transaction_status(self, transaction_id: int, status: PaymentStatus) -> Optional[TokenTransaction]:
        """Update transaction status"""
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return None
        
        transaction.status = status
        if status == PaymentStatus.COMPLETED:
            transaction.processed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    # Token Package Operations
    def get_packages(self, active_only: bool = True) -> List[TokenPackage]:
        """Get all token packages"""
        query = self.db.query(TokenPackage)
        if active_only:
            query = query.filter(TokenPackage.is_active == True)
        return query.all()

    def get_package(self, package_id: int) -> Optional[TokenPackage]:
        """Get package by ID"""
        return self.db.query(TokenPackage).filter(TokenPackage.id == package_id).first()

    def create_package(self, **kwargs) -> TokenPackage:
        """Create new token package"""
        package = TokenPackage(**kwargs)
        package.total_tokens = package.tokens_included + package.bonus_tokens
        self.db.add(package)
        self.db.commit()
        self.db.refresh(package)
        return package

    # Subscription Operations
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
