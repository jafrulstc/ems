"""
routers/auth.py
---------------
Thin router: only handles HTTP layer (request/response).
Business logic lives in AuthService.
"""

from typing import Any, Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep, TenantDep
from app.schemas.auth import Token, UserCreate, UserRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Any:
    """
    OAuth2-compatible login.
    Email is globally unique — tenant is resolved automatically.
    Returns JWT token + tenant slug + branch_id.
    """
    return await AuthService.login(
        email=form_data.username,
        password=form_data.password,
        session=session,
    )


@router.post("/register", response_model=UserRead)
async def register(
    session: SessionDep,
    tenant: TenantDep,
    user_in: UserCreate,
) -> Any:
    """Register a new user under the current tenant."""
    return await AuthService.register_user(user_in, tenant, session)
