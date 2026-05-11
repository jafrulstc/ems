"""
Permission repository — global permissions + RBAC resolution.

RBAC resolution order (per plan A5):
  1. user_permission_overrides  → override always wins (grant or deny)
  2. role_permissions via user's roles → any granted role suffices
  3. → DENIED
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.models import (
    Permission, RolePermission, UserPermissionOverride, UserRole,
)


class PermissionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_all(self) -> list[Permission]:
        r = await self._db.execute(
            select(Permission).order_by(Permission.module, Permission.key)
        )
        return list(r.scalars().all())

    async def get_by_keys(self, keys: list[str]) -> list[Permission]:
        r = await self._db.execute(select(Permission).where(Permission.key.in_(keys)))
        return list(r.scalars().all())

    async def get_overrides(self, user_id: int, org_id: int) -> list[UserPermissionOverride]:
        r = await self._db.execute(
            select(UserPermissionOverride).where(
                UserPermissionOverride.user_id == user_id,
                UserPermissionOverride.organization_id == org_id,
            )
        )
        return list(r.scalars().all())

    async def upsert_override(
        self, user_id: int, org_id: int, permission_id: int, is_granted: bool
    ) -> UserPermissionOverride:
        r = await self._db.execute(
            select(UserPermissionOverride).where(
                UserPermissionOverride.user_id == user_id,
                UserPermissionOverride.permission_id == permission_id,
            )
        )
        obj = r.scalar_one_or_none()
        if obj:
            obj.is_granted = is_granted
        else:
            obj = UserPermissionOverride(
                user_id=user_id, organization_id=org_id,
                permission_id=permission_id, is_granted=is_granted,
            )
            self._db.add(obj)
        await self._db.flush()
        return obj

    async def resolve(self, user_id: int, org_id: int, permission_key: str) -> bool:
        """Returns True if the user has the given permission."""
        # Step 1: override
        override_stmt = (
            select(UserPermissionOverride.is_granted)
            .join(Permission, UserPermissionOverride.permission_id == Permission.id)
            .where(
                UserPermissionOverride.user_id == user_id,
                UserPermissionOverride.organization_id == org_id,
                Permission.key == permission_key,
            )
        )
        override = (await self._db.execute(override_stmt)).scalar_one_or_none()
        if override is not None:
            return bool(override)

        # Step 2: role permissions
        role_stmt = (
            select(func.count())
            .select_from(UserRole)
            .join(RolePermission, UserRole.role_id == RolePermission.role_id)
            .join(Permission, RolePermission.permission_id == Permission.id)
            .where(UserRole.user_id == user_id, Permission.key == permission_key)
        )
        count = (await self._db.execute(role_stmt)).scalar_one()
        return count > 0

    async def resolve_all(self, user_id: int, org_id: int) -> list[str]:
        """Return all resolved permission keys for a user.

        Logic:
          1. Collect permission keys from every role the user holds.
          2. Apply user_permission_overrides: granted adds, denied removes.
        """
        # Step 1: role-based permission keys
        role_stmt = (
            select(Permission.key)
            .distinct()
            .select_from(UserRole)
            .join(RolePermission, UserRole.role_id == RolePermission.role_id)
            .join(Permission, RolePermission.permission_id == Permission.id)
            .where(UserRole.user_id == user_id)
        )
        role_rows = await self._db.execute(role_stmt)
        granted: set[str] = set(role_rows.scalars().all())

        # Step 2: overrides — always win over role permissions
        override_stmt = (
            select(Permission.key, UserPermissionOverride.is_granted)
            .join(Permission, UserPermissionOverride.permission_id == Permission.id)
            .where(
                UserPermissionOverride.user_id == user_id,
                UserPermissionOverride.organization_id == org_id,
            )
        )
        override_rows = await self._db.execute(override_stmt)
        for key, is_granted in override_rows.all():
            if is_granted:
                granted.add(key)
            else:
                granted.discard(key)

        return sorted(granted)
