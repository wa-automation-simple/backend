"""API routes __init__ for Auth service."""

from auth.api.v1.users import router as users_router

__all__ = ["users_router"]
