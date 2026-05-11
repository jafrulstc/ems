"""Auth service — login, refresh, logout."""
from jose import JWTError

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.features.auth.repositories.permission_repo import PermissionRepository
from app.features.auth.repositories.user_repo import UserRepository
from app.features.auth.schemas import LoginRequest, LoginResponse, UserMeResponse, UserRead
from app.features.auth.security import (
    create_access_token, create_refresh_token, decode_token, verify_password,
)
from app.shared.exceptions import unauthorized

settings = get_settings()


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = UserRepository(db)

    async def login(self, payload: LoginRequest) -> tuple[LoginResponse, str]:
        """Returns (LoginResponse, refresh_token_str)."""
        org = await self._repo.get_org_by_slug(payload.org_slug)
        if not org or not org.is_active:
            raise unauthorized("Invalid credentials.")

        user = await self._repo.get_by_email(payload.email, org.id)
        if not user or not user.is_active:
            raise unauthorized("Invalid credentials.")

        if not verify_password(payload.password, user.hashed_password):
            raise unauthorized("Invalid credentials.")

        role_ids = await self._repo.get_role_ids(user.id)
        access = create_access_token(user.id, org.id, role_ids, user.is_superuser)
        refresh = create_refresh_token(user.id, org.id)

        # Reload with roles for response
        user_full = await self._repo.get_by_id(user.id, org.id)
        return LoginResponse(
            access_token=access,
            user=UserRead.model_validate(user_full),
        ), refresh

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        """Returns (new_access_token, new_refresh_token)."""
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise unauthorized("Invalid refresh token.")

        if payload.get("type") != "refresh":
            raise unauthorized("Invalid token type.")

        user_id = int(payload["sub"])
        org_id = int(payload["org"])

        user = await self._repo.get_by_id(user_id, org_id)
        if not user or not user.is_active:
            raise unauthorized("User not found or inactive.")

        role_ids = await self._repo.get_role_ids(user_id)
        new_access = create_access_token(user_id, org_id, role_ids, user.is_superuser)
        new_refresh = create_refresh_token(user_id, org_id)
        return new_access, new_refresh

    async def get_me(self, user_id: int, org_id: int) -> UserMeResponse:
        user = await self._repo.get_by_id(user_id, org_id)
        if not user:
            raise unauthorized("User not found.")
        permissions = await PermissionRepository(self._db).resolve_all(user_id, org_id)
        return UserMeResponse(
            **UserRead.model_validate(user).model_dump(),
            permissions=permissions,
        )
