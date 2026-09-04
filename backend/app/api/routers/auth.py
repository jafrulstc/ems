"""
routers/auth.py
---------------
Thin router: only handles HTTP layer (request/response).
Business logic lives in AuthService.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.api.deps import SessionDep, TenantDep
from app.core.security import get_password_hash
from app.models.auth import User
from app.schemas.auth import Token, UserCreate, UserRead, UserUpdate
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


@router.get("/users", response_model=list[UserRead])
async def read_users(
    session: SessionDep,
    tenant: TenantDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve users under the current tenant."""
    stmt = select(User).where(User.tenant_id == tenant.id).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.put("/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    session: SessionDep,
    tenant: TenantDep,
    user_in: UserUpdate,
) -> Any:
    """Update a user."""
    stmt = select(User).where(User.id == user_id, User.tenant_id == tenant.id)
    db_user = (await session.execute(stmt)).scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
    for k, v in update_data.items():
        setattr(db_user, k, v)
        
    await session.commit()
    await session.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    session: SessionDep,
    tenant: TenantDep,
) -> Any:
    """Delete a user."""
    stmt = select(User).where(User.id == user_id, User.tenant_id == tenant.id)
    db_user = (await session.execute(stmt)).scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db_user.is_deleted = True
    await session.commit()
    return {"message": "User deleted successfully"}
