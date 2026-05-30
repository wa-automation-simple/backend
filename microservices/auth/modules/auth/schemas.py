from pydantic import BaseModel, EmailStr
from uuid import UUID


class RegisterRequest(BaseModel):
    username: str
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    name: str
    email: str
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
