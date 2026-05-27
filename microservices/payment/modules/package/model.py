"""Token Package Model"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from payment.config import Base


class TokenPackage(Base):
    __tablename__ = "token_packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    
    # Package details
    tokens_included = Column(Integer, nullable=False)
    base_price = Column(Float, nullable=False)  # $3 per token base
    sell_price = Column(Float, nullable=False)  # Markup price (e.g., $10 per token)
    discount_percentage = Column(Float, default=0.0)  # Bulk discount
    
    # Bonus
    bonus_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, nullable=False)  # tokens_included + bonus_tokens
    
    is_active = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)  # Mark as recommended
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TokenPackage(name={self.name}, tokens={self.total_tokens})>"
