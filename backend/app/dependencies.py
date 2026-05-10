"""
FastAPI shared dependencies.

Provides injectable dependencies used across all feature routers:
  - get_current_user()       : resolves User from request.state (set by TenantMiddleware)
  - require_permission(key)  : RBAC factory dependency — raises HTTP 403 if denied
  - get_organization_id()    : extracts organization_id from request.state
"""
from typing import Callable

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.shared.exceptions import forbidden, unauthorized


# ── Current user context ──────────────────────────────────────────────────────

class CurrentUser:
    """Lightweight DTO populated from JWT claims on request.state."""

    def __init__(self, user_id: int, organization_id: int, roles: list[int]) -> None:
        self.user_id = user_id
        self.organization_id = organization_id
        self.roles = roles


async def get_current_user(request: Request) -> CurrentUser:
    """
    Dependency that extracts the authenticated user context from request.state.
    TenantMiddleware must have already populated it.
    """
    user_id: int | None = getattr(request.state, "user_id", None)
    org_id: int | None = getattr(request.state, "organization_id", None)
    if user_id is None or org_id is None:
        raise unauthorized()
    return CurrentUser(
        user_id=user_id,
        organization_id=org_id,
        roles=getattr(request.state, "roles", []),
    )


async def get_organization_id(
    current_user: CurrentUser = Depends(get_current_user),
) -> int:
    """Shorthand dependency — returns just the organization_id int."""
    return current_user.organization_id


# ── RBAC ──────────────────────────────────────────────────────────────────────

def require_permission(permission_key: str) -> Callable:
    """
    RBAC dependency factory.  Usage:

        @router.post("/items", dependencies=[Depends(require_permission("academic.students.create"))])

    Resolution order (per plan A5):
      1. user_permission_overrides  → override always wins
      2. role_permissions           → any granted role suffices
      3. HTTP 403

    The actual DB check is deferred to Phase 3 (auth module).
    During Phase 1 this is a structural stub that always allows — it will be
    replaced with the full async DB query once the auth models exist.
    """

    async def _check(
        request: Request,
        db: AsyncSession = Depends(get_db),
        current_user: CurrentUser = Depends(get_current_user),
    ) -> None:
        # ── Phase 3 will replace the body below with real RBAC logic ──────
        # Superuser bypass is handled in auth_service; here we trust the JWT.
        # For Phase 1, we simply verify the user is authenticated (done above).
        pass  # pragma: no cover — real impl injected in Phase 3

    return _check
