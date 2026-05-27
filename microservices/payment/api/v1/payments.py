"""Payment API Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from payment.api.deps import get_payment_service
from payment.services.payment_service import PaymentService
from payment.schemas.serializers import (
    TokenBalanceResponse,
    TokenPackageResponse,
    TokenTopup,
    TokenTransactionResponse,
    PaymentCreate,
    PaymentResponse,
    SubscriptionCreate,
    SubscriptionResponse
)

router = APIRouter(prefix="/api/v1", tags=["payments"])


@router.get("/balance", response_model=TokenBalanceResponse)
def get_balance(
    current_user_id: int = 1,  # TODO: Get from JWT token
    service: PaymentService = Depends(get_payment_service)
):
    """Get user token balance"""
    return service.get_balance(current_user_id)


@router.get("/packages", response_model=List[TokenPackageResponse])
def get_packages(service: PaymentService = Depends(get_payment_service)):
    """Get all available token packages"""
    return service.get_packages()


@router.post("/topup")
def purchase_tokens(
    data: TokenTopup,
    current_user_id: int = 1,  # TODO: Get from JWT token
    service: PaymentService = Depends(get_payment_service)
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
    service: PaymentService = Depends(get_payment_service)
):
    """Complete payment after gateway confirmation"""
    try:
        return service.complete_payment(transaction_id, payment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/transactions", response_model=List[TokenTransactionResponse])
def get_transactions(
    current_user_id: int = 1,  # TODO: Get from JWT token
    service: PaymentService = Depends(get_payment_service)
):
    """Get user transaction history"""
    return service.get_transactions(current_user_id)


@router.post("/deduct")
def deduct_tokens(
    tokens: int,
    description: str = None,
    ai_reply_id: int = None,
    current_user_id: int = 1,  # TODO: Get from JWT token
    service: PaymentService = Depends(get_payment_service)
):
    """Deduct tokens (for AI usage)"""
    try:
        return service.deduct_tokens(current_user_id, tokens, description, ai_reply_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/subscription", response_model=SubscriptionResponse)
def create_subscription(
    data: SubscriptionCreate,
    current_user_id: int = 1,  # TODO: Get from JWT token
    service: PaymentService = Depends(get_payment_service)
):
    """Create monthly subscription"""
    return service.create_subscription(current_user_id, data)


@router.post("/subscription/{subscription_id}/cancel")
def cancel_subscription(
    subscription_id: int,
    service: PaymentService = Depends(get_payment_service)
):
    """Cancel subscription"""
    return service.cancel_subscription(subscription_id)
