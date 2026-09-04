"""
auth_service.py
---------------
Business logic for authentication and user management.
"""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.auth import User
from app.models.tenant import Institute


class AuthService:
    # ── Login ─────────────────────────────────────────────────────────────────

    @staticmethod
    async def login(email: str, password: str, session: AsyncSession) -> dict:
        """
        Authenticate a user by email (globally unique).
        Returns access token, tenant slug and branch_id.
        """
        stmt = (
            select(User, Institute)
            .join(Institute, User.tenant_id == Institute.id)
            .where(User.email == email)
        )
        row = (await session.execute(stmt)).first()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password",
            )

        user, tenant = row

        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )

        access_token = create_access_token(
            subject=user.id,
            tenant_id=tenant.id,
            branch_id=user.branch_id,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "tenant_slug": tenant.slug,
            "branch_id": str(user.branch_id) if user.branch_id else None,
        }

    # ── Register ──────────────────────────────────────────────────────────────

    @staticmethod
    async def register_user(user_in, tenant: Institute, session: AsyncSession) -> User:
        """
        Register a new user under the given tenant.
        Raises 400 if email already exists in the tenant.
        """
        exists = (
            await session.execute(
                select(User).where(
                    User.email == user_in.email,
                    User.tenant_id == tenant.id,
                )
            )
        ).scalar_one_or_none()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists.",
            )

        user_data = user_in.model_dump(exclude={"password"})
        db_user = User(
            **user_data,
            hashed_password=get_password_hash(user_in.password),
            tenant_id=tenant.id,
        )
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user
