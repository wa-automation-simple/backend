"""Token Wallet Routes"""
from fastapi import APIRouter, Depends
from payment.models.wallet.service import WalletService
from payment.models.wallet.schemas import TokenBalanceResponse

router = APIRouter(prefix="/wallet", tags=["wallet"])


def get_wallet_service(db):
    """Dependency to get wallet service"""
    from sqlalchemy.orm import Session
    from payment.core.database import SessionLocal
    db = SessionLocal()
    try:
        return WalletService(db)
    finally:
        db.close()


@router.get("/balance/{user_id}", response_model=TokenBalanceResponse)
def get_balance(
    user_id: int,
    service: WalletService = Depends(get_wallet_service)
):
    """Get user token balance"""
    return service.get_balance(user_id)
