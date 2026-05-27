"""Auth Service Schemas - Django-like serializers for request/response validation"""

# Re-export from shared schemas to maintain consistency
from shared.schemas.serializers import (
    UserCreate,
    UserResponse,
    UserUpdate,
    TokenRequest,
    TokenResponse,
    PasswordChange
)

__all__ = [
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "TokenRequest",
    "TokenResponse",
    "PasswordChange"
]
