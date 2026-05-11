"""
Auth feature router. Prefix: /api/v1/auth
"""
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user, get_organization_id, require_permission
from app.features.auth.schemas import (
    LoginRequest, LoginResponse, PermissionOverrideRead, PermissionOverrideUpsert,
    PermissionRead, RoleCreate, RoleUpdate, RoleWithPermissions,
    UserCreate, UserMeResponse, UserRead, UserUpdate,
)
from app.features.auth.services.auth_service import AuthService
from app.features.auth.services.permission_service import PermissionService
from app.features.auth.services.role_service import RoleService
from app.features.auth.services.user_service import UserService
from app.shared.exceptions import unauthorized
from app.shared.pagination import PaginationParams, pagination_params
from app.shared.schemas import APIResponse, PaginatedResponse, ok, paginated

router = APIRouter()
settings = get_settings()
_COOKIE = "refresh_token"
_COOKIE_MAX_AGE = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=_COOKIE, value=token, httponly=True,
        samesite="strict", secure=settings.is_production,
        max_age=_COOKIE_MAX_AGE,
    )


# ── Auth ──────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=APIResponse[LoginResponse], tags=["Auth"])
async def login(payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    login_resp, refresh = await svc.login(payload)
    _set_refresh_cookie(response, refresh)
    return ok(login_resp, "Login successful.")


@router.post("/refresh", response_model=APIResponse[dict], tags=["Auth"])
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get(_COOKIE)
    if not token:
        raise unauthorized("No refresh token provided.")
    new_access, new_refresh = await AuthService(db).refresh(token)
    _set_refresh_cookie(response, new_refresh)
    return ok({"access_token": new_access, "token_type": "bearer"})


@router.post("/logout", response_model=APIResponse[None], tags=["Auth"])
async def logout(response: Response):
    response.delete_cookie(_COOKIE)
    return ok(None, "Logged out successfully.")


@router.get("/me", response_model=APIResponse[UserMeResponse], tags=["Auth"])
async def me(request: Request, db: AsyncSession = Depends(get_db),
             cu=Depends(get_current_user)):
    return ok(await AuthService(db).get_me(cu.user_id, cu.organization_id))


# ── Users ─────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=PaginatedResponse[UserRead], tags=["Users"])
async def list_users(p: PaginationParams = Depends(pagination_params),
                     org_id: int = Depends(get_organization_id),
                     db: AsyncSession = Depends(get_db),
                     _=Depends(require_permission("auth.users.view"))):
    data = await UserService(db).list(org_id, p)
    return paginated(data.items, data.total, data.page, data.size)


@router.post("/users", response_model=APIResponse[UserRead], status_code=201, tags=["Users"])
async def create_user(payload: UserCreate, org_id: int = Depends(get_organization_id),
                      db: AsyncSession = Depends(get_db),
                      _=Depends(require_permission("auth.users.create"))):
    return ok(await UserService(db).create(org_id, payload), "User created.")


@router.get("/users/{id}", response_model=APIResponse[UserRead], tags=["Users"])
async def get_user(id: int, org_id: int = Depends(get_organization_id),
                   db: AsyncSession = Depends(get_db),
                   _=Depends(require_permission("auth.users.view"))):
    return ok(await UserService(db).get(id, org_id))


@router.put("/users/{id}", response_model=APIResponse[UserRead], tags=["Users"])
async def update_user(id: int, payload: UserUpdate,
                      org_id: int = Depends(get_organization_id),
                      db: AsyncSession = Depends(get_db),
                      _=Depends(require_permission("auth.users.edit"))):
    return ok(await UserService(db).update(id, org_id, payload))


@router.delete("/users/{id}", response_model=APIResponse[None], tags=["Users"])
async def delete_user(id: int, org_id: int = Depends(get_organization_id),
                      db: AsyncSession = Depends(get_db),
                      _=Depends(require_permission("auth.users.delete"))):
    await UserService(db).delete(id, org_id)
    return ok(None, "User deleted.")


@router.get("/users/{id}/overrides", response_model=APIResponse[list[PermissionOverrideRead]], tags=["Users"])
async def get_overrides(id: int, org_id: int = Depends(get_organization_id),
                        db: AsyncSession = Depends(get_db),
                        _=Depends(require_permission("auth.users.edit"))):
    return ok(await PermissionService(db).get_overrides(id, org_id))


@router.put("/users/{id}/overrides", response_model=APIResponse[list[PermissionOverrideRead]], tags=["Users"])
async def upsert_overrides(id: int, payload: list[PermissionOverrideUpsert],
                           org_id: int = Depends(get_organization_id),
                           db: AsyncSession = Depends(get_db),
                           _=Depends(require_permission("auth.users.edit"))):
    return ok(await PermissionService(db).upsert_overrides(id, org_id, payload))


@router.put("/users/{id}/roles", response_model=APIResponse[UserRead], tags=["Users"])
async def set_user_roles(id: int, role_ids: list[int],
                         org_id: int = Depends(get_organization_id),
                         db: AsyncSession = Depends(get_db),
                         _=Depends(require_permission("auth.users.edit"))):
    """Assign roles to a user."""
    return ok(await UserService(db).set_roles(id, org_id, role_ids))


# ── Roles ─────────────────────────────────────────────────────────────────────

@router.get("/roles", response_model=APIResponse[list[RoleWithPermissions]], tags=["Roles"])
async def list_roles(org_id: int = Depends(get_organization_id),
                     db: AsyncSession = Depends(get_db),
                     _=Depends(require_permission("auth.roles.view"))):
    return ok(await RoleService(db).list(org_id))


@router.post("/roles", response_model=APIResponse[RoleWithPermissions], status_code=201, tags=["Roles"])
async def create_role(payload: RoleCreate, org_id: int = Depends(get_organization_id),
                      db: AsyncSession = Depends(get_db),
                      _=Depends(require_permission("auth.roles.create"))):
    return ok(await RoleService(db).create(org_id, payload), "Role created.")


@router.put("/roles/{id}", response_model=APIResponse[RoleWithPermissions], tags=["Roles"])
async def update_role(id: int, payload: RoleUpdate,
                      org_id: int = Depends(get_organization_id),
                      db: AsyncSession = Depends(get_db),
                      _=Depends(require_permission("auth.roles.edit"))):
    return ok(await RoleService(db).update(id, org_id, payload))


@router.delete("/roles/{id}", response_model=APIResponse[None], tags=["Roles"])
async def delete_role(id: int, org_id: int = Depends(get_organization_id),
                      db: AsyncSession = Depends(get_db),
                      _=Depends(require_permission("auth.roles.delete"))):
    await RoleService(db).delete(id, org_id)
    return ok(None, "Role deleted.")


@router.post("/roles/{id}/permissions", response_model=APIResponse[RoleWithPermissions], tags=["Roles"])
async def assign_permissions(id: int, permission_keys: list[str],
                             org_id: int = Depends(get_organization_id),
                             db: AsyncSession = Depends(get_db),
                             _=Depends(require_permission("auth.roles.edit"))):
    return ok(await RoleService(db).assign_permissions(id, org_id, permission_keys))


# ── Permissions ───────────────────────────────────────────────────────────────

@router.get("/permissions", response_model=APIResponse[list[PermissionRead]], tags=["Permissions"])
async def list_permissions(db: AsyncSession = Depends(get_db),
                           _=Depends(require_permission("auth.permissions.view"))):
    return ok(await PermissionService(db).list_all())
