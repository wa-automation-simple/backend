from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from google.oauth2 import id_token
from google.auth.transport import requests

from modules.user.model import User
from modules.role.model import Role

from middleware.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
)

from modules.auth.schemas import RegisterRequest, AuthResponse, UserResponse

from core.config import settings
import uuid


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

    async def login_google(self, credential):
        # 1. Verify Google ID token
        google_user = id_token.verify_oauth2_token(
            credential, requests.Request(), settings.GOOGLE_CLIENT_ID
        )
        # if not email:
        #     raise HTTPException(status_code=400, detail="Invalid Google account")

        user = await self._get_or_create_user(google_user)

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

        # 5. Return to frontend
        # return {
        #     "access_token": access_token,
        #     "refresh_token": refresh_token,
        #     "user": {
        #         "id": user.id,
        #         "email": user.email,
        #         "name": user.name,
        #         "avatar": user.avatar,
        #     },
        # }

        return AuthResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def _generate_username(self, email: str) -> str:
        base = email.split("@")[0]
        base = "".join(c for c in base if c.isalnum() or c == ".").lower()
        suffix = uuid.uuid4().hex[:6]
        return f"{base}_{suffix}"

    async def _get_or_create_user(self, google_user: dict):
        google_sub = google_user.get("sub")
        email = google_user.get("email")
        name = google_user.get("name")
        picture = google_user.get("picture")

        user = await self.db.scalar(select(User).where(User.google_sub == google_sub))

        if not user:
            user = await self.db.scalar(select(User).where(User.email == email))

        if user:
            user.google_sub = google_sub
            user.google_email = email
            user.google_name = name
            user.google_picture = picture
            user.google_account_connected = True
        else:
            user = User(
                email=email,
                username=self._generate_username(email),
                name=name,
                google_sub=google_sub,
                google_email=email,
                google_name=name,
                google_picture=picture,
                google_account_connected=True,
            )
            self.db.add(user)

        await self.db.commit()
        await self.db.refresh(user)

        return user
