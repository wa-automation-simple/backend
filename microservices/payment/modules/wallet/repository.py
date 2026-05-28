"""Token Wallet Repository"""
from sqlalchemy.orm import Session
from typing import Optional
from payment.modules.wallet.model import TokenWallet
from datetime import datetime


class WalletRepository:
    def __init__(self, db: Session):
        self.db = db

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
