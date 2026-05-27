"""API routes __init__ for WhatsApp service."""

from whatsapp.api.v1.accounts import router as accounts_router

__all__ = ["accounts_router"]
