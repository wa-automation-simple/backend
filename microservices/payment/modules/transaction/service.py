"""Token Transaction Service"""
from typing import List, Optional
from sqlalchemy.orm import Session
from payment.modules.transaction.repository import TransactionRepository
from payment.modules.wallet.service import WalletService
from payment.modules.transaction.schemas import TokenTopup, PaymentCreate
from payment.modules.transaction.enums import PaymentStatus
from payment.config import settings


class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TransactionRepository(db)
        self.wallet_service = WalletService(db)

    def purchase_tokens(self, user_id: int, data: TokenTopup):
        """Purchase tokens (create pending transaction)"""
        wallet = self.wallet_service.get_or_create_wallet(user_id)
        
        if data.package_id:
            from payment.modules.package.service import PackageService
            package_service = PackageService(self.db)
            package = package_service.get_package(data.package_id)
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
        self.wallet_service.update_balance(transaction.wallet_id, total_tokens)

        return transaction

    def get_transactions(self, user_id: int) -> List:
        """Get user transaction history"""
        return self.repo.get_user_transactions(user_id)

    def deduct_tokens(self, user_id: int, tokens: int, description: str = None, ai_reply_id: int = None):
        """Deduct tokens from wallet (for AI usage)"""
        wallet = self.wallet_service.get_or_create_wallet(user_id)
        
        if wallet.balance < tokens:
            raise ValueError("Insufficient token balance")

        # Deduct from wallet
        self.wallet_service.update_balance(wallet.id, -tokens)

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
