"""Follow-up API Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from followup.api.deps import get_followup_service
from followup.services.followup_service import FollowUpService
from followup.schemas.serializers import (
    LeadCreate, LeadUpdate, LeadResponse,
    InteractionLogCreate, InteractionLogResponse,
    FollowUpSequenceCreate, FollowUpSequenceResponse
)

router = APIRouter(prefix="/api/v1", tags=["followups"])


@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(
    data: LeadCreate,
    whatsapp_account_id: int,
    current_user_id: int = 1,
    service: FollowUpService = Depends(get_followup_service)
):
    """Create new lead for follow-up"""
    return service.create_lead(current_user_id, whatsapp_account_id, data)


@router.get("/leads", response_model=List[LeadResponse])
def get_leads(
    status: str = None,
    current_user_id: int = 1,
    service: FollowUpService = Depends(get_followup_service)
):
    """Get leads for user"""
    return service.get_leads(current_user_id, status)


@router.get("/leads/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    service: FollowUpService = Depends(get_followup_service)
):
    """Get lead by ID"""
    lead = service.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/leads/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    data: LeadUpdate,
    service: FollowUpService = Depends(get_followup_service)
):
    """Update lead"""
    lead = service.update_lead(lead_id, data)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/leads/{lead_id}/interactions", response_model=InteractionLogResponse)
def log_interaction(
    lead_id: int,
    data: InteractionLogCreate,
    whatsapp_account_id: int,
    current_user_id: int = 1,
    service: FollowUpService = Depends(get_followup_service)
):
    """Log interaction with lead"""
    data.lead_id = lead_id
    return service.log_interaction(current_user_id, whatsapp_account_id, data)


@router.get("/leads/{lead_id}/interactions", response_model=List[InteractionLogResponse])
def get_interactions(
    lead_id: int,
    service: FollowUpService = Depends(get_followup_service)
):
    """Get interactions for lead"""
    return service.get_interactions(lead_id)


@router.post("/leads/{lead_id}/followup")
def perform_followup(
    lead_id: int,
    interval_days: int = 3,
    service: FollowUpService = Depends(get_followup_service)
):
    """Perform follow-up and schedule next one"""
    result = service.perform_followup(lead_id, interval_days)
    if not result:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"message": "Follow-up performed", "lead": result}


@router.get("/followups/due", response_model=List[LeadResponse])
def get_due_followups(
    current_user_id: int = 1,
    service: FollowUpService = Depends(get_followup_service)
):
    """Get leads due for follow-up"""
    return service.get_due_followups(current_user_id)


@router.post("/sequences", response_model=FollowUpSequenceResponse)
def create_sequence(
    data: FollowUpSequenceCreate,
    current_user_id: int = 1,
    service: FollowUpService = Depends(get_followup_service)
):
    """Create follow-up sequence"""
    return service.create_sequence(current_user_id, data)


@router.get("/sequences", response_model=List[FollowUpSequenceResponse])
def get_sequences(
    current_user_id: int = 1,
    service: FollowUpService = Depends(get_followup_service)
):
    """Get sequences for user"""
    return service.get_sequences(current_user_id)
