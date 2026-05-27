"""Token Wallet Service"""
from typing import Optional
from sqlalchemy.orm import Session
from payment.models.wallet.repository import WalletRepository
from payment.models.wallet.schemas import TokenBalanceResponse


class WalletService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = WalletRepository(db)

    def get_or_create_wallet(self, user_id: int):
        """Get or create token wallet for user"""
        wallet = self.repo.get_wallet_by_user(user_id)
        if not wallet:
            wallet = self.repo.create_wallet(user_id)
        return wallet

    def get_balance(self, user_id: int) -> TokenBalanceResponse:
        """Get user token balance"""
        wallet = self.get_or_create_wallet(user_id)
        return TokenBalanceResponse(
            user_id=user_id,
            balance=wallet.balance,
            reserved_tokens=wallet.reserved_tokens,
            available_tokens=wallet.balance - wallet.reserved_tokens,
            price_per_token=wallet.price_per_token,
            estimated_value_usd=wallet.balance * wallet.price_per_token
        )

    def update_balance(self, wallet_id: int, tokens: int):
        """Update wallet balance"""
        return self.repo.update_balance(wallet_id, tokens)
