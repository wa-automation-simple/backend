"""WhatsApp account management routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from whatsapp.core.database import get_db
from whatsapp.schemas.serializers import (
    WhatsAppAccountCreate,
    WhatsAppAccountResponse,
    WhatsAppAccountUpdate,
    WarmupStart,
    WarmupStatusResponse,
    MessageSendRequest,
    MessageSendWithMedia,
    MessageLogResponse,
    AccountsListResponse,
    MessagesListResponse
)
from whatsapp.services.account_service import WhatsAppAccountService
from whatsapp.api.deps import get_account_service


router = APIRouter(prefix="/accounts", tags=["WhatsApp Accounts"])


@router.post("/", response_model=WhatsAppAccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account_data: WhatsAppAccountCreate,
    service: WhatsAppAccountService = Depends(get_account_service)
):
    """Create a new WhatsApp account for multi-account support."""
    try:
        account = service.create_account(
            user_id=account_data.user_id,
            phone_number=account_data.phone_number,
            account_name=account_data.account_name,
            is_primary=account_data.is_primary
        )
        return account
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=AccountsListResponse)
def list_accounts(
    user_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    service: WhatsAppAccountService = Depends(get_account_service)
):
    """List WhatsApp accounts with optional filters."""
    accounts, total = service.list_accounts(user_id=user_id, page=page, page_size=page_size)
    
    return AccountsListResponse(
        accounts=[WhatsAppAccountResponse.model_validate(a) for a in accounts],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{account_id}", response_model=WhatsAppAccountResponse)
def get_account(
    account_id: int,
    service: WhatsAppAccountService = Depends(get_account_service)
):
    """Get WhatsApp account by ID."""
    account = service.get_account(account_id)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return account


@router.put("/{account_id}", response_model=WhatsAppAccountResponse)
def update_account(
    account_id: int,
    account_data: WhatsAppAccountUpdate,
    service: WhatsAppAccountService = Depends(get_account_service)
):
    """Update WhatsApp account information."""
    update_data = {k: v for k, v in account_data.model_dump().items() if v is not None}
    
    account = service.update_account(account_id, **update_data)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return account


@router.delete("/{account_id}")
def delete_account(
    account_id: int,
    service: WhatsAppAccountService = Depends(get_account_service)
):
    """Delete a WhatsApp account."""
    success = service.delete_account(account_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return {"message": "Account deleted successfully"}


@router.post("/{account_id}/warmup", response_model=dict)
def start_warmup(
    account_id: int,
    warmup_data: WarmupStart,
    service: WhatsAppAccountService = Depends(get_account_service)
):
    """Start the 30-day warmup process for an account (Panasin WA)."""
    try:
        result = service.start_warmup(account_id, warmup_data.duration_days)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{account_id}/warmup/status", response_model=WarmupStatusResponse)
def get_warmup_status(
    account_id: int,
    service: WhatsAppAccountService = Depends(get_account_service)
):
    """Get current warmup status for an account."""
    status_data = service.get_warmup_status(account_id)
    
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No warmup schedule found for this account"
        )
    
    return WarmupStatusResponse(**status_data)


@router.post("/{account_id}/messages", response_model=dict)
def send_message(
    account_id: int,
    message_data: MessageSendRequest,
    service: WhatsAppAccountService = Depends(get_account_service)
):
    """Send a text message from a WhatsApp account."""
    try:
        result = service.send_message(
            account_id=account_id,
            recipient=message_data.recipient,
            content=message_data.content,
            message_type="text"
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{account_id}/messages/media", response_model=dict)
def send_message_with_media(
    account_id: int,
    message_data: MessageSendWithMedia,
    service: WhatsAppAccountService = Depends(get_account_service)
):
    """Send a message with media (image/video/audio/document)."""
    try:
        result = service.send_message(
            account_id=account_id,
            recipient=message_data.recipient,
            content=message_data.content,
            message_type=message_data.media_type,
            media_url=str(message_data.media_url)
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{account_id}/messages", response_model=MessagesListResponse)
def get_message_logs(
    account_id: int,
    page: int = 1,
    page_size: int = 50,
    service: WhatsAppAccountService = Depends(get_account_service)
):
    """Get message logs for a WhatsApp account."""
    messages, total = service.get_message_logs(account_id, page, page_size)
    
    return MessagesListResponse(
        messages=[MessageLogResponse.model_validate(m) for m in messages],
        total=total,
        page=page,
        page_size=page_size
    )
