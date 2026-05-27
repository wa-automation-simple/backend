from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from whatsapp_service.config.database import get_db
from whatsapp_service.services.whatsapp_service import (
    create_whatsapp_account,
    get_whatsapp_accounts_by_user,
    get_whatsapp_account,
    update_whatsapp_account,
    delete_whatsapp_account,
    start_warming,
    stop_warming,
    get_warming_status,
    increment_warming_day,
    set_recovery_link
)
from shared.schemas.serializers import (
    WhatsAppAccountCreate,
    WhatsAppAccountResponse,
    WhatsAppAccountUpdate,
    WarmupStart,
    WarmupStatus,
    RecoveryLinkResponse,
    AutoClickRequest,
    MessageResponse
)
from shared.utils.auth import get_current_user, require_permission
from shared.models.rbac import PermissionEnum

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Accounts"])


@router.post("/accounts", response_model=WhatsAppAccountResponse, status_code=status.HTTP_201_CREATED)
def add_whatsapp_account(
    account_data: WhatsAppAccountCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new WhatsApp account (Multi-account support)"""
    account = create_whatsapp_account(
        db=db,
        user_id=current_user["user_id"],
        phone_number=account_data.phone_number
    )
    return account


@router.get("/accounts", response_model=List[WhatsAppAccountResponse])
def list_whatsapp_accounts(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all WhatsApp accounts for the current user"""
    accounts = get_whatsapp_accounts_by_user(db, current_user["user_id"])
    return accounts


@router.get("/accounts/{account_id}", response_model=WhatsAppAccountResponse)
def get_account(
    account_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific WhatsApp account"""
    account = get_whatsapp_account(db, account_id, current_user["user_id"])
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    return account


@router.put("/accounts/{account_id}", response_model=WhatsAppAccountResponse)
def update_account(
    account_id: int,
    account_update: WhatsAppAccountUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update WhatsApp account settings"""
    account = get_whatsapp_account(db, account_id, current_user["user_id"])
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    
    update_data = account_update.dict(exclude_unset=True)
    updated_account = update_whatsapp_account(db, account_id, **update_data)
    return updated_account


@router.delete("/accounts/{account_id}", response_model=MessageResponse)
def delete_account(
    account_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete WhatsApp account"""
    success = delete_whatsapp_account(db, account_id, current_user["user_id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    return MessageResponse(message="WhatsApp account deleted successfully")


# Warming endpoints
@router.post("/warmup/start", response_model=WhatsAppAccountResponse)
def start_account_warmup(
    warmup_data: WarmupStart,
    current_user: dict = Depends(require_permission(PermissionEnum.WA_WARMUP_START)),
    db: Session = Depends(get_db)
):
    """Start warming process for a WhatsApp account"""
    account = get_whatsapp_account(db, warmup_data.whatsapp_account_id, current_user["user_id"])
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    
    warmed_account = start_warming(db, warmup_data.whatsapp_account_id)
    return warmed_account


@router.post("/warmup/stop", response_model=WhatsAppAccountResponse)
def stop_account_warmup(
    warmup_data: WarmupStart,
    current_user: dict = Depends(require_permission(PermissionEnum.WA_WARMUP_STOP)),
    db: Session = Depends(get_db)
):
    """Stop warming process for a WhatsApp account"""
    account = get_whatsapp_account(db, warmup_data.whatsapp_account_id, current_user["user_id"])
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    
    warmed_account = stop_warming(db, warmup_data.whatsapp_account_id)
    return warmed_account


@router.get("/warmup/status/{account_id}", response_model=WarmupStatus)
def get_warmup_status(
    account_id: int,
    current_user: dict = Depends(require_permission(PermissionEnum.WA_WARMUP_READ)),
    db: Session = Depends(get_db)
):
    """Get warming status for a WhatsApp account"""
    account = get_whatsapp_account(db, account_id, current_user["user_id"])
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    
    status_data = get_warming_status(db, account_id)
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warming status not found"
        )
    
    return WarmupStatus(**status_data)


@router.post("/warmup/increment-day", response_model=MessageResponse)
def increment_warming_day_endpoint(
    warmup_data: WarmupStart,
    current_user: dict = Depends(require_permission(PermissionEnum.WA_WARMUP_READ)),
    db: Session = Depends(get_db)
):
    """Manually increment warming day (for testing/demo)"""
    account = get_whatsapp_account(db, warmup_data.whatsapp_account_id, current_user["user_id"])
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    
    account = increment_warming_day(db, warmup_data.whatsapp_account_id)
    return MessageResponse(message=f"Warming day incremented to {account.warming_day}")


# Recovery endpoints
@router.get("/recovery-link/{account_id}", response_model=RecoveryLinkResponse)
def get_recovery_link(
    account_id: int,
    current_user: dict = Depends(require_permission(PermissionEnum.RECOVERY_MANAGE)),
    db: Session = Depends(get_db)
):
    """Get recovery link for banned WhatsApp account"""
    account = get_whatsapp_account(db, account_id, current_user["user_id"])
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    
    if not account.recovery_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recovery link available"
        )
    
    return RecoveryLinkResponse(
        whatsapp_account_id=account_id,
        recovery_link=account.recovery_link,
        auto_click_enabled=account.auto_click_enabled
    )


@router.post("/auto-click/toggle", response_model=MessageResponse)
def toggle_auto_click(
    request: AutoClickRequest,
    current_user: dict = Depends(require_permission(PermissionEnum.AUTO_CLICK_ENABLE)),
    db: Session = Depends(get_db)
):
    """Enable/disable auto-click for recovery link"""
    account = get_whatsapp_account(db, request.whatsapp_account_id, current_user["user_id"])
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    
    update_whatsapp_account(db, request.whatsapp_account_id, auto_click_enabled=request.enabled)
    action = "enabled" if request.enabled else "disabled"
    return MessageResponse(message=f"Auto-click {action} for account {request.whatsapp_account_id}")


@router.post("/recovery/set-link", response_model=MessageResponse)
def set_account_recovery_link(
    account_id: int,
    recovery_link: str,
    current_user: dict = Depends(require_permission(PermissionEnum.RECOVERY_MANAGE)),
    db: Session = Depends(get_db)
):
    """Set recovery link for banned account (called by WhatsApp integration)"""
    account = get_whatsapp_account(db, account_id, current_user["user_id"])
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp account not found"
        )
    
    set_recovery_link(db, account_id, recovery_link)
    return MessageResponse(message="Recovery link set successfully")
