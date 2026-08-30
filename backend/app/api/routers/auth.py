from typing import Any, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.api.deps import SessionDep, TenantDep
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.auth import User
from app.schemas.auth import Token, UserCreate, UserRead

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    session: SessionDep,
    tenant: TenantDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    stmt = select(User).where(User.email == form_data.username, User.tenant_id == tenant.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token = create_access_token(subject=user.id, tenant_id=tenant.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserRead)
async def register_user(
    session: SessionDep,
    tenant: TenantDep,
    user_in: UserCreate
) -> Any:
    """
    Register new user.
    """
    stmt = select(User).where(User.email == user_in.email, User.tenant_id == tenant.id)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user_data = user_in.model_dump(exclude={"password"})
    hashed_password = get_password_hash(user_in.password)
    
    db_user = User(
        **user_data,
        hashed_password=hashed_password,
        tenant_id=tenant.id
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user
