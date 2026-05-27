"""FollowUp module - Auto-generated."""

from followup.modules.follow_up.model import FollowUp
from followup.modules.follow_up.schemas import FollowUpCreate, FollowUpUpdate, FollowUpResponse
from followup.modules.follow_up.repository import FollowUpRepository
from followup.modules.follow_up.service import FollowUpService
from followup.modules.follow_up.routes import router

__all__ = [
    "FollowUp",
    "FollowUpCreate",
    "FollowUpUpdate",
    "FollowUpResponse",
    "FollowUpRepository",
    "FollowUpService",
    "router",
]
