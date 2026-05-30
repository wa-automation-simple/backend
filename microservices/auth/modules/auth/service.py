from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.model import User
from modules.role.model import Role

from middleware.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
)

from modules.auth.schemas import RegisterRequest, AuthResponse, UserResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(
        self,
        payload: RegisterRequest,
    ) -> AuthResponse:

        existing_user = await self.db.scalar(
            select(User).where(
                or_(
                    User.email == payload.email,
                    User.username == payload.username,
                )
            )
        )

        if existing_user:
            if existing_user.email == payload.email:
                raise ValueError("Email already registered")

            if existing_user.username == payload.username:
                raise ValueError("Username already taken")

        user = User(
            username=payload.username,
            name=payload.name,
            email=payload.email,
            hashed_password=get_password_hash(payload.password),
            is_active=True,
            is_verified=False,
        )

        self.db.add(user)

        await self.db.flush()
        await self.db.refresh(user)

        role = await self.db.scalar(select(Role).where(Role.name == "user"))

        if not role:
            raise ValueError("Default role not found")

        # user.roles.append(role)
        user.roles = [role]

        await self.db.commit()
        await self.db.refresh(user)

        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "username": user.username,
            }
        )

        refresh_token = create_refresh_token(
            data={
                "sub": str(user.id),
            }
        )

        return AuthResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def login(
        self,
        email: str,
        password: str,
    ) -> AuthResponse:

        user = await self.db.scalar(select(User).where(User.email == email))

        if not user:
            raise ValueError("Invalid credentials")

        if not verify_password(
            password,
            user.hashed_password,
        ):
            raise ValueError("Invalid credentials")

        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "username": user.username,
            }
        )

        refresh_token = create_refresh_token(
            data={
                "sub": str(user.id),
            }
        )

        return AuthResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
        )
