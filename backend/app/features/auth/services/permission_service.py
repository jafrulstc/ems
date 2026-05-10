"""Permission service — list all permissions + manage per-user overrides."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.repositories.permission_repo import PermissionRepository
from app.features.auth.repositories.user_repo import UserRepository
from app.features.auth.schemas import (
    PermissionOverrideRead, PermissionOverrideUpsert, PermissionRead,
)
from app.shared.exceptions import bad_request, not_found


class PermissionService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = PermissionRepository(db)
        self._user_repo = UserRepository(db)

    async def list_all(self) -> list[PermissionRead]:
        items = await self._repo.get_all()
        return [PermissionRead.model_validate(p) for p in items]

    async def get_overrides(self, user_id: int, org_id: int) -> list[PermissionOverrideRead]:
        # Verify user exists in org
        user = await self._user_repo.get_by_id(user_id, org_id)
        if not user:
            raise not_found("User")
        items = await self._repo.get_overrides(user_id, org_id)
        return [PermissionOverrideRead.model_validate(i) for i in items]

    async def upsert_overrides(
        self, user_id: int, org_id: int, overrides: list[PermissionOverrideUpsert]
    ) -> list[PermissionOverrideRead]:
        user = await self._user_repo.get_by_id(user_id, org_id)
        if not user:
            raise not_found("User")
        keys = [o.permission_key for o in overrides]
        perms = await self._repo.get_by_keys(keys)
        perm_map = {p.key: p.id for p in perms}
        missing = [k for k in keys if k not in perm_map]
        if missing:
            raise bad_request(f"Unknown permission keys: {missing}")
        results = []
        for override in overrides:
            obj = await self._repo.upsert_override(
                user_id, org_id, perm_map[override.permission_key], override.is_granted
            )
            results.append(PermissionOverrideRead.model_validate(obj))
        return results
