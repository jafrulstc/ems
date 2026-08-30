from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import SessionDep, require_permission, TenantDep
from app.models.tenant import Institute, Branch
from app.models.auth import User
from app.core.security import get_password_hash
from app.schemas.tenant import InstituteCreate, InstituteRead, InstituteUpdate, BranchCreate, BranchRead

router = APIRouter()

@router.post("/institutes", response_model=InstituteRead)
async def create_institute(
    session: SessionDep,
    institute_in: InstituteCreate
) -> Any:
    # Notice: create_institute is a global operation, typically protected by a super_admin check
    # For now, we allow it so you can create the first institute
    stmt = select(Institute).where(Institute.slug == institute_in.slug)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Institute with this slug already exists")
        
    db_institute = Institute(
        name=institute_in.name,
        slug=institute_in.slug,
        address=institute_in.address,
        contact_email=institute_in.contact_email
    )
    session.add(db_institute)
    await session.flush()
    
    admin_user = User(
        email=institute_in.admin_email,
        hashed_password=get_password_hash(institute_in.admin_password),
        full_name=f"Admin of {institute_in.name}",
        user_type="admin",
        tenant_id=db_institute.id
    )
    session.add(admin_user)
    
    await session.commit()
    await session.refresh(db_institute)
    return db_institute

@router.get("/institutes", response_model=list[InstituteRead])
async def read_institutes(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    stmt = select(Institute).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.post("/branches", response_model=BranchRead, dependencies=[Depends(require_permission("branch:create"))])
async def create_branch(
    session: SessionDep,
    tenant: TenantDep,
    branch_in: BranchCreate
) -> Any:
    db_branch = Branch(**branch_in.model_dump(), tenant_id=tenant.id)
    session.add(db_branch)
    await session.commit()
    await session.refresh(db_branch)
    return db_branch

@router.get("/branches", response_model=list[BranchRead], dependencies=[Depends(require_permission("branch:read"))])
async def read_branches(
    session: SessionDep,
    tenant: TenantDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    stmt = select(Branch).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()

@router.put("/institutes/{institute_id}", response_model=InstituteRead)
async def update_institute(institute_id: str, session: SessionDep, institute_in: InstituteUpdate) -> Any:
    db = (await session.execute(select(Institute).where(Institute.id == institute_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Institute not found")
    
    update_data = institute_in.model_dump(exclude_unset=True)
    admin_email = update_data.pop("admin_email", None)
    admin_password = update_data.pop("admin_password", None)
    
    for k, v in update_data.items(): setattr(db, k, v)
    
    if admin_email or admin_password:
        admin_user = (await session.execute(select(User).where(User.tenant_id == db.id, User.user_type == "admin"))).scalars().first()
        if admin_user:
            if admin_email: admin_user.email = admin_email
            if admin_password: admin_user.hashed_password = get_password_hash(admin_password)
        else:
            if admin_email and admin_password:
                admin_user = User(
                    email=admin_email,
                    hashed_password=get_password_hash(admin_password),
                    full_name=f"Admin of {db.name}",
                    user_type="admin",
                    tenant_id=db.id
                )
                session.add(admin_user)
            
    await session.commit(); await session.refresh(db); return db

@router.delete("/institutes/{institute_id}")
async def delete_institute(institute_id: str, session: SessionDep) -> Any:
    db = (await session.execute(select(Institute).where(Institute.id == institute_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Institute not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}

@router.put("/branches/{branch_id}", response_model=BranchRead, dependencies=[Depends(require_permission("branch:update"))])
async def update_branch(branch_id: str, session: SessionDep, tenant: TenantDep, branch_in: BranchCreate) -> Any:
    db = (await session.execute(select(Branch).where(Branch.id == branch_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Branch not found")
    for k, v in branch_in.model_dump().items(): setattr(db, k, v)
    await session.commit(); await session.refresh(db); return db

@router.delete("/branches/{branch_id}", dependencies=[Depends(require_permission("branch:delete"))])
async def delete_branch(branch_id: str, session: SessionDep, tenant: TenantDep) -> Any:
    db = (await session.execute(select(Branch).where(Branch.id == branch_id))).scalar_one_or_none()
    if not db: raise HTTPException(status_code=404, detail="Branch not found")
    db.is_deleted = True; await session.commit(); return {"message": "Deleted"}
