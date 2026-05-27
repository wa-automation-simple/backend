"""
Payment Service - Token top-up and payment processing
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from shared.utils.database import get_db, engine, Base
from shared.schemas.serializers import (
    PaymentCreate, PaymentResponse, TokenBalanceResponse, MessageResponse
)
from shared.models.tables import User, Payment, TokenBalance, TokenTransaction
from shared.models.rbac import RequirePermission
from shared.config.settings import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Payment Service",
    description="Payment Processing and Token Top-up",
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
    return {"status": "healthy", "service": "payment-service"}


@app.post("/payments", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(RequirePermission("payment:create")),
    db: Session = Depends(get_db)
):
    """Create new payment/top-up request"""
    # Calculate tokens based on markup pricing
    tokens_to_add = payment_data.tokens_purchased
    
    payment = Payment(
        user_id=current_user.id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method,
        tokens_purchased=tokens_to_add,
        status="pending"
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # In production, integrate with Stripe/PayPal here
    # For demo, auto-complete the payment
    payment.status = "completed"
    payment.transaction_id = f"TXN_{payment.id}_{settings.JWT_SECRET_KEY[:8]}"
    
    # Update token balance
    balance = db.query(TokenBalance).filter(
        TokenBalance.user_id == current_user.id
    ).first()
    
    if not balance:
        balance = TokenBalance(user_id=current_user.id, balance=0.0)
        db.add(balance)
    
    balance.balance += payment_data.amount
    balance.total_purchased += payment_data.amount
    
    # Record transaction
    transaction = TokenTransaction(
        token_balance_id=balance.id,
        amount=payment_data.amount,
        transaction_type="purchase",
        description=f"Payment via {payment_data.payment_method}"
    )
    db.add(transaction)
    db.commit()
    db.refresh(payment)
    
    return payment


@app.get("/payments", response_model=List[PaymentResponse])
async def list_payments(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(RequirePermission("payment:read")),
    db: Session = Depends(get_db)
):
    """List all payments for current user"""
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    return payments


@app.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(RequirePermission("payment:read")),
    db: Session = Depends(get_db)
):
    """Get specific payment"""
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.user_id == current_user.id
    ).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return payment


@app.get("/pricing", response_model=dict)
async def get_pricing_info():
    """Get token pricing information (showing markup)"""
    return {
        "base_price_per_token": settings.TOKEN_BASE_PRICE,  # $3 (cost from provider)
        "sell_price_per_token": settings.TOKEN_SELL_PRICE,   # $10 (price to user)
        "markup_percentage": ((settings.TOKEN_SELL_PRICE - settings.TOKEN_BASE_PRICE) / settings.TOKEN_BASE_PRICE) * 100,
        "packages": [
            {"tokens": 10, "price": 10 * settings.TOKEN_SELL_PRICE, "savings": 0},
            {"tokens": 50, "price": 50 * settings.TOKEN_SELL_PRICE * 0.95, "savings": "5%"},
            {"tokens": 100, "price": 100 * settings.TOKEN_SELL_PRICE * 0.90, "savings": "10%"},
            {"tokens": 500, "price": 500 * settings.TOKEN_SELL_PRICE * 0.85, "savings": "15%"},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
