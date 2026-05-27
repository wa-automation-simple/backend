"""Token Transaction Model"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum
from datetime import datetime
from payment.core.database import Base
from payment.models.transaction.enums import PaymentStatus


class TokenTransaction(Base):
    __tablename__ = "token_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    wallet_id = Column(Integer, ForeignKey("token_wallets.id"), nullable=False)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # purchase, usage, refund, transfer
    tokens_amount = Column(Integer, nullable=False)
    unit_price = Column(Float, default=10.0)
    total_amount = Column(Float, nullable=False)  # In USD
    
    # Payment reference
    payment_id = Column(String(255), nullable=True)  # External payment gateway ID
    payment_method = Column(String(50))  # stripe, paypal, bank_transfer
    
    # Token package info
    package_name = Column(String(100), nullable=True)  # e.g., "Starter Pack", "Pro Pack"
    bonus_tokens = Column(Integer, default=0)  # Bonus tokens from promotions
    
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    description = Column(Text, nullable=True)
    
    # AI usage tracking
    ai_reply_id = Column(Integer, nullable=True)  # Reference to AI reply that used tokens
    tokens_used_for_ai = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<TokenTransaction(id={self.id}, type={self.transaction_type}, amount={self.tokens_amount})>"
