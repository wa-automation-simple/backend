"""
AI Service - Auto-reply with AI, token management with markup pricing
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from shared.utils.database import get_db, engine, Base
from shared.schemas.serializers import (
    AutoReplyCreate, AutoReplyResponse, AutoReplyUpdate,
    AIRequest, AIResponse, TokenBalanceResponse, TokenTopup,
    TokenTransactionResponse, MessageResponse
)
from shared.models.tables import User, AutoReply, TokenBalance, TokenTransaction
from shared.models.rbac import RequirePermission
from shared.config.settings import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Service",
    description="AI Auto-Reply and Token Management with Markup Pricing",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-service"}


# ============== AUTO REPLY ENDPOINTS ==============

@app.post("/auto-reply", response_model=AutoReplyResponse)
async def create_auto_reply(
    reply_data: AutoReplyCreate,
    current_user: User = Depends(RequirePermission("auto_reply:create")),
    db: Session = Depends(get_db)
):
    """Create auto-reply rule (with optional AI)"""
    reply = AutoReply(
        user_id=current_user.id,
        whatsapp_account_id=reply_data.whatsapp_account_id,
        trigger_keyword=reply_data.trigger_keyword,
        response_message=reply_data.response_message,
        use_ai=reply_data.use_ai,
        ai_context=reply_data.ai_context,
        priority=reply_data.priority
    )
    
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply


@app.get("/auto-reply", response_model=List[AutoReplyResponse])
async def list_auto_replies(
    current_user: User = Depends(RequirePermission("auto_reply:read")),
    db: Session = Depends(get_db)
):
    """List all auto-reply rules"""
    replies = db.query(AutoReply).filter(
        AutoReply.user_id == current_user.id
    ).all()
    return replies


@app.put("/auto-reply/{reply_id}", response_model=AutoReplyResponse)
async def update_auto_reply(
    reply_id: int,
    reply_update: AutoReplyUpdate,
    current_user: User = Depends(RequirePermission("auto_reply:update")),
    db: Session = Depends(get_db)
):
    """Update auto-reply rule"""
    reply = db.query(AutoReply).filter(
        AutoReply.id == reply_id,
        AutoReply.user_id == current_user.id
    ).first()
    if not reply:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auto-reply not found"
        )
    
    if reply_update.trigger_keyword is not None:
        reply.trigger_keyword = reply_update.trigger_keyword
    if reply_update.response_message is not None:
        reply.response_message = reply_update.response_message
    if reply_update.use_ai is not None:
        reply.use_ai = reply_update.use_ai
    if reply_update.ai_context is not None:
        reply.ai_context = reply_update.ai_context
    if reply_update.is_active is not None:
        reply.is_active = reply_update.is_active
    if reply_update.priority is not None:
        reply.priority = reply_update.priority
    
    db.commit()
    db.refresh(reply)
    return reply


@app.delete("/auto-reply/{reply_id}", response_model=MessageResponse)
async def delete_auto_reply(
    reply_id: int,
    current_user: User = Depends(RequirePermission("auto_reply:delete")),
    db: Session = Depends(get_db)
):
    """Delete auto-reply rule"""
    reply = db.query(AutoReply).filter(
        AutoReply.id == reply_id,
        AutoReply.user_id == current_user.id
    ).first()
    if not reply:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auto-reply not found"
        )
    
    db.delete(reply)
    db.commit()
    return MessageResponse(message="Auto-reply deleted successfully")


# ============== AI PROCESSING ENDPOINTS ==============

@app.post("/ai/generate", response_model=AIResponse)
async def generate_ai_response(
    request_data: AIRequest,
    current_user: User = Depends(RequirePermission("ai:use")),
    db: Session = Depends(get_db)
):
    """Generate AI response for incoming message"""
    # Get user's token balance
    token_balance = db.query(TokenBalance).filter(
        TokenBalance.user_id == current_user.id
    ).first()
    
    if not token_balance or token_balance.balance <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient token balance. Please top up."
        )
    
    # Calculate tokens needed (simplified)
    tokens_needed = 1.0  # 1 message = 1 token
    cost = tokens_needed * settings.TOKEN_SELL_PRICE  # $10 per token (markup from $3)
    
    if token_balance.balance < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient balance. Need ${cost}, have ${token_balance.balance}"
        )
    
    # Generate AI response (in production, call OpenAI API)
    ai_response = f"[AI] Based on your message '{request_data.message}', here's a helpful response..."
    
    if request_data.context:
        ai_response += f"\nContext considered: {request_data.context}"
    
    # Deduct tokens
    token_balance.balance -= cost
    token_balance.total_used += cost
    
    # Record transaction
    transaction = TokenTransaction(
        token_balance_id=token_balance.id,
        amount=-cost,
        transaction_type="usage",
        description=f"AI response for: {request_data.message[:50]}"
    )
    db.add(transaction)
    db.commit()
    
    return AIResponse(
        response=ai_response,
        tokens_used=tokens_needed,
        cost=cost
    )


# ============== TOKEN MANAGEMENT ENDPOINTS ==============

@app.get("/tokens/balance", response_model=TokenBalanceResponse)
async def get_token_balance(
    current_user: User = Depends(RequirePermission("token:view")),
    db: Session = Depends(get_db)
):
    """Get current token balance"""
    balance = db.query(TokenBalance).filter(
        TokenBalance.user_id == current_user.id
    ).first()
    
    if not balance:
        # Create balance record if doesn't exist
        balance = TokenBalance(user_id=current_user.id, balance=0.0)
        db.add(balance)
        db.commit()
        db.refresh(balance)
    
    return TokenBalanceResponse(
        user_id=balance.user_id,
        balance=balance.balance,
        total_purchased=balance.total_purchased,
        total_used=balance.total_used,
        base_price_per_token=settings.TOKEN_BASE_PRICE,  # $3
        sell_price_per_token=settings.TOKEN_SELL_PRICE   # $10 (markup)
    )


@app.post("/tokens/topup", response_model=TokenBalanceResponse)
async def topup_tokens(
    topup_data: TokenTopup,
    current_user: User = Depends(RequirePermission("token:topup")),
    db: Session = Depends(get_db)
):
    """Top up token balance (with markup pricing)"""
    # Get or create token balance
    balance = db.query(TokenBalance).filter(
        TokenBalance.user_id == current_user.id
    ).first()
    
    if not balance:
        balance = TokenBalance(user_id=current_user.id, balance=0.0)
        db.add(balance)
    
    # Calculate tokens to add based on markup pricing
    # User pays $10 per token, but we show base price is $3
    tokens_to_add = topup_data.amount / settings.TOKEN_SELL_PRICE
    
    # Update balance
    balance.balance += tokens_to_add * settings.TOKEN_SELL_PRICE  # Add in dollar value
    balance.total_purchased += topup_data.amount
    
    # Record transaction
    transaction = TokenTransaction(
        token_balance_id=balance.id,
        amount=topup_data.amount,
        transaction_type="purchase",
        description=f"Topup via {topup_data.payment_method}"
    )
    db.add(transaction)
    db.commit()
    db.refresh(balance)
    
    return TokenBalanceResponse(
        user_id=balance.user_id,
        balance=balance.balance,
        total_purchased=balance.total_purchased,
        total_used=balance.total_used,
        base_price_per_token=settings.TOKEN_BASE_PRICE,
        sell_price_per_token=settings.TOKEN_SELL_PRICE
    )


@app.get("/tokens/transactions", response_model=List[TokenTransactionResponse])
async def get_token_transactions(
    limit: int = 50,
    current_user: User = Depends(RequirePermission("token:view")),
    db: Session = Depends(get_db)
):
    """Get token transaction history"""
    balance = db.query(TokenBalance).filter(
        TokenBalance.user_id == current_user.id
    ).first()
    
    if not balance:
        return []
    
    transactions = db.query(TokenTransaction).filter(
        TokenTransaction.token_balance_id == balance.id
    ).order_by(TokenTransaction.created_at.desc()).limit(limit).all()
    
    return transactions


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
