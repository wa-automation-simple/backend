"""
Payment Service - Token top-up and payment processing
Handles: payment processing, token purchase, pricing markup ($3 -> $10)
"""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from shared.database import get_db
from shared.models import Transaction, TokenBalance, User
from shared.schemas import TopUpRequest, TransactionResponse
from shared.config import settings

app = FastAPI(title="Payment Service", version="1.0.0")


class PaymentProcessor:
    """Mock payment processor"""
    
    def __init__(self):
        self.supported_methods = ["credit_card", "paypal", "crypto", "bank_transfer"]
    
    async def process_payment(
        self,
        amount: float,
        payment_method: str,
        user_id: int
    ) -> dict:
        """Process payment (mock implementation)"""
        if payment_method not in self.supported_methods:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported payment method. Supported: {', '.join(self.supported_methods)}"
            )
        
        # Simulate payment processing
        success = True  # In production, integrate with actual payment gateway
        
        if success:
            return {
                "success": True,
                "transaction_id": f"txn_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "amount": amount,
                "payment_method": payment_method,
                "status": "completed"
            }
        else:
            return {
                "success": False,
                "transaction_id": None,
                "amount": amount,
                "payment_method": payment_method,
                "status": "failed"
            }


payment_processor = PaymentProcessor()


def calculate_tokens(amount: float) -> float:
    """Calculate tokens purchased based on amount with markup pricing"""
    # Base price is $3 per 1000 tokens
    # Markup price is $10 per 1000 tokens (what users pay)
    tokens_per_dollar = 1000 / settings.TOKEN_MARKUP_PRICE
    return amount * tokens_per_dollar


@app.post("/topup", response_model=TransactionResponse)
async def top_up_tokens(
    topup_data: TopUpRequest,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Top up token balance"""
    # Calculate tokens to be added
    tokens_purchased = calculate_tokens(topup_data.amount)
    
    # Process payment
    payment_result = await payment_processor.process_payment(
        amount=topup_data.amount,
        payment_method=topup_data.payment_method,
        user_id=user_id
    )
    
    if not payment_result["success"]:
        raise HTTPException(status_code=400, detail="Payment failed")
    
    # Create transaction record
    transaction = Transaction(
        user_id=user_id,
        amount=topup_data.amount,
        tokens_purchased=tokens_purchased,
        payment_method=topup_data.payment_method,
        status="completed"
    )
    db.add(transaction)
    
    # Update token balance
    token_balance = db.query(TokenBalance).filter(
        TokenBalance.user_id == user_id
    ).first()
    
    if not token_balance:
        # Create new balance record
        token_balance = TokenBalance(user_id=user_id, balance=tokens_purchased)
        db.add(token_balance)
    else:
        token_balance.balance += tokens_purchased
        token_balance.last_updated = datetime.now()
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


@app.get("/transactions", response_model=List[TransactionResponse])
async def list_transactions(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List user's transaction history"""
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(
        Transaction.transaction_date.desc()
    ).offset(offset).limit(limit).all()
    
    return transactions


@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Get transaction details"""
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction


@app.get("/pricing")
async def get_pricing():
    """Get current pricing information"""
    return {
        "base_cost_per_1000_tokens": settings.TOKEN_BASE_PRICE,
        "user_price_per_1000_tokens": settings.TOKEN_MARKUP_PRICE,
        "markup_percentage": ((settings.TOKEN_MARKUP_PRICE - settings.TOKEN_BASE_PRICE) / settings.TOKEN_BASE_PRICE) * 100,
        "currency": "USD",
        "packages": [
            {
                "name": "Starter",
                "price": 10,
                "tokens": 1000,
                "bonus": 0
            },
            {
                "name": "Professional",
                "price": 50,
                "tokens": 5000,
                "bonus": 500  # 10% bonus
            },
            {
                "name": "Business",
                "price": 100,
                "tokens": 10000,
                "bonus": 2000  # 20% bonus
            },
            {
                "name": "Enterprise",
                "price": 500,
                "tokens": 50000,
                "bonus": 15000  # 30% bonus
            }
        ],
        "payment_methods": payment_processor.supported_methods
    }


@app.post("/packages/{package_name}/purchase")
async def purchase_package(
    package_name: str,
    user_id: int,
    payment_method: str,
    db: Session = Depends(get_db)
):
    """Purchase a token package"""
    packages = {
        "starter": {"price": 10, "tokens": 1000, "bonus": 0},
        "professional": {"price": 50, "tokens": 5000, "bonus": 500},
        "business": {"price": 100, "tokens": 10000, "bonus": 2000},
        "enterprise": {"price": 500, "tokens": 50000, "bonus": 15000}
    }
    
    if package_name.lower() not in packages:
        raise HTTPException(
            status_code=404,
            detail=f"Package not found. Available: {', '.join(packages.keys())}"
        )
    
    package = packages[package_name.lower()]
    total_tokens = package["tokens"] + package["bonus"]
    
    # Process payment
    payment_result = await payment_processor.process_payment(
        amount=package["price"],
        payment_method=payment_method,
        user_id=user_id
    )
    
    if not payment_result["success"]:
        raise HTTPException(status_code=400, detail="Payment failed")
    
    # Create transaction
    transaction = Transaction(
        user_id=user_id,
        amount=package["price"],
        tokens_purchased=total_tokens,
        payment_method=payment_method,
        status="completed"
    )
    db.add(transaction)
    
    # Update balance
    token_balance = db.query(TokenBalance).filter(
        TokenBalance.user_id == user_id
    ).first()
    
    if not token_balance:
        token_balance = TokenBalance(user_id=user_id, balance=total_tokens)
        db.add(token_balance)
    else:
        token_balance.balance += total_tokens
        token_balance.last_updated = datetime.now()
    
    db.commit()
    db.refresh(transaction)
    
    return {
        "transaction": transaction,
        "package": package_name,
        "base_tokens": package["tokens"],
        "bonus_tokens": package["bonus"],
        "total_tokens": total_tokens,
        "amount_paid": package["price"]
    }


@app.get("/balance/{user_id}")
async def get_balance(user_id: int, db: Session = Depends(get_db)):
    """Get user's current token balance"""
    balance = db.query(TokenBalance).filter(
        TokenBalance.user_id == user_id
    ).first()
    
    if not balance:
        return {
            "user_id": user_id,
            "balance": 0,
            "tokens_used": 0,
            "message": "No token balance found. Please top up."
        }
    
    return {
        "user_id": user_id,
        "balance": balance.balance,
        "tokens_used": balance.tokens_used,
        "last_updated": balance.last_updated
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
