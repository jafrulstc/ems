import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.context import branch_context, tenant_context, user_context
from app.db.session import get_db
from app.models.auth import User
from app.models.tenant import Institute
from app.schemas.auth import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

SessionDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]

async def get_tenant_from_slug(request: Request, db: SessionDep) -> Institute:
    slug = request.headers.get("X-Tenant-Slug")
    if not slug:
        raise HTTPException(status_code=400, detail="X-Tenant-Slug header missing")
    
    stmt = select(Institute).where(Institute.slug == slug)
    result = await db.execute(stmt)
    institute = result.scalar_one_or_none()
    
    if not institute:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    tenant_context.set(institute.id)
    return institute

TenantDep = Annotated[Institute, Depends(get_tenant_from_slug)]

async def get_current_user(db: SessionDep, token: TokenDep, tenant: TenantDep) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenPayload(**payload)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    if token_data.tenant_id != str(tenant.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch in token")
        
    stmt = select(User).where(User.id == uuid.UUID(token_data.sub), User.tenant_id == tenant.id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    # Set both user and branch context for downstream use
    user_context.set(user)
    if user.branch_id:
        branch_context.set(user.branch_id)
        
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

def require_permission(perm_name: str):
    async def permission_checker(current_user: CurrentUser, db: SessionDep) -> User:
        if current_user.user_type in ("super_admin", "admin"):
            return current_user
            
        if current_user.role_id:
            from app.models.auth import Permission, RolePermission
            stmt = (
                select(Permission.name)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .where(RolePermission.role_id == current_user.role_id)
            )
            result = await db.execute(stmt.execution_options(skip_rlac=True))
            permissions = result.scalars().all()
            if perm_name in permissions:
                return current_user
                
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Requires permission: {perm_name}")
    return permission_checker
