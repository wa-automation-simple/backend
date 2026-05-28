"""Token Transaction Repository"""
from sqlalchemy.orm import Session
from typing import List, Optional
from payment.modules.transaction.transaction import TokenTransaction
from payment.modules.transaction.enums import PaymentStatus
from datetime import datetime


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

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
