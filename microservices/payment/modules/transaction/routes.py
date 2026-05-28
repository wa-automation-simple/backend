"""Token Transaction Routes"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from payment.modules.transaction.service import TransactionService
from payment.modules.transaction.schemas import (
    TokenTopup, 
    TokenTransactionResponse, 
    PaymentCreate,
    PaymentResponse
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


def get_transaction_service():
    """Dependency to get transaction service"""
    from sqlalchemy.orm import Session
    from payment.config import SessionLocal
    db = SessionLocal()
    try:
        return TransactionService(db)
    finally:
        db.close()


@router.post("/topup")
def purchase_tokens(
    data: TokenTopup,
    current_user_id: int = 1,  # TODO: Get from JWT token
    service: TransactionService = Depends(get_transaction_service)
):
    """Purchase tokens"""
    try:
        return service.purchase_tokens(current_user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/topup/{transaction_id}/complete")
def complete_payment(
    transaction_id: int,
    payment_id: str,
    service: TransactionService = Depends(get_transaction_service)
):
    """Complete payment after gateway confirmation"""
    try:
        return service.complete_payment(transaction_id, payment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/user/{user_id}", response_model=List[TokenTransactionResponse])
def get_transactions(
    user_id: int,
    service: TransactionService = Depends(get_transaction_service)
):
    """Get user transaction history"""
    return service.get_transactions(user_id)


@router.post("/deduct")
def deduct_tokens(
    tokens: int,
    description: str = None,
    ai_reply_id: int = None,
    current_user_id: int = 1,  # TODO: Get from JWT token
    service: TransactionService = Depends(get_transaction_service)
):
    """Deduct tokens (for AI usage)"""
    try:
        return service.deduct_tokens(current_user_id, tokens, description, ai_reply_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
