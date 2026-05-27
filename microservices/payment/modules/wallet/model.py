"""Token Wallet Model"""
from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime
from payment.config import Base


class TokenWallet(Base):
    __tablename__ = "token_wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    
    # Balance tracking
    balance = Column(Integer, default=0)  # Number of tokens
    reserved_tokens = Column(Integer, default=0)  # Tokens reserved for pending operations
    
    # Pricing tier
    price_per_token = Column(Float, default=10.0)  # Markup price
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TokenWallet(user_id={self.user_id}, balance={self.balance})>"
