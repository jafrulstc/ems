"""
Tenant resolution middleware.

Resolves the current tenant (Organization) from the JWT access token and
attaches it to `request.state.organization_id` so that all downstream
dependencies and repositories can scope queries without re-reading the token.

Strategy
--------
1. Public paths (login, refresh, docs, healthz, geo) are excluded.
2. For all other paths the `Authorization: Bearer <token>` header is decoded.
3. The `org` claim is extracted and stored on request.state.
4. If the token is absent or invalid on a protected path, HTTP 401 is raised.

Note: Full RBAC enforcement is handled by `require_permission()` in
      dependencies.py — this middleware only sets the context.
"""
import logging
from typing import Set

from fastapi import Request, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Paths that do not require a tenant context
_PUBLIC_PREFIXES: Set[str] = {
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/core/geo",   # geographic reference data is public
    "/docs",
    "/redoc",
    "/openapi.json",
    "/healthz",
}


def _is_public(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in _PUBLIC_PREFIXES)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Starlette middleware that resolves `organization_id` from the JWT payload
    and attaches it to `request.state` before the route handler runs.
    """

    async def dispatch(self, request: Request, call_next):
        if _is_public(request.url.path):
            return await call_next(request)

        auth_header: str | None = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Authentication required.", "data": None},
            )

        token = auth_header.removeprefix("Bearer ").strip()
        try:
            payload = jwt.decode(
                token,
                settings.APP_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            organization_id: int | None = payload.get("org")
            if organization_id is None:
                raise JWTError("Missing 'org' claim")
            request.state.organization_id = int(organization_id)
            request.state.user_id = int(payload.get("sub", 0))
            request.state.roles = payload.get("roles", [])
        except JWTError as exc:
            logger.debug("JWT decode failed: %s", exc)
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Invalid or expired token.", "data": None},
            )

        return await call_next(request)
