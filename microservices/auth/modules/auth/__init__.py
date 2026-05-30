"""Permission module initialization."""

from modules.auth.schemas import AuthResponse, LoginRequest, RegisterRequest
from modules.auth.service import AuthService
from modules.auth.routes import router

__all__ = [
    "AuthReponse",
    "LoginRequest",
    "RegisterRequest",
    "AuthSerice",
    "router",
]
