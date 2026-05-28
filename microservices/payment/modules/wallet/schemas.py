"""Token Wallet Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TokenBalanceResponse(BaseModel):
    """Serializer for token balance response"""
    user_id: int
    balance: int
    reserved_tokens: int
    available_tokens: int
    price_per_token: float
    estimated_value_usd: float
