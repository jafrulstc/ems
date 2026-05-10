"""Role management service."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.repositories.permission_repo import PermissionRepository
from app.features.auth.repositories.role_repo import RoleRepository
from app.features.auth.schemas import RoleCreate, RoleUpdate, RoleWithPermissions
from app.shared.exceptions import not_found


class RoleService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = RoleRepository(db)
        self._perm_repo = PermissionRepository(db)

    async def list(self, org_id: int) -> list[RoleWithPermissions]:
        items = await self._repo.get_many(org_id)
        return [RoleWithPermissions.model_validate(r) for r in items]

    async def get(self, id: int, org_id: int) -> RoleWithPermissions:
        role = await self._repo.get_by_id(id, org_id)
        if not role:
            raise not_found("Role")
        return RoleWithPermissions.model_validate(role)

    async def create(self, org_id: int, payload: RoleCreate) -> RoleWithPermissions:
        role = await self._repo.create(org_id, payload.model_dump())
        return RoleWithPermissions.model_validate(role)

    async def update(self, id: int, org_id: int, payload: RoleUpdate) -> RoleWithPermissions:
        role = await self._repo.get_by_id(id, org_id)
        if not role:
            raise not_found("Role")
        role = await self._repo.update(role, payload.model_dump(exclude_none=True))
        return RoleWithPermissions.model_validate(role)

    async def delete(self, id: int, org_id: int) -> None:
        role = await self._repo.get_by_id(id, org_id)
        if not role:
            raise not_found("Role")
        await self._repo.soft_delete(role)

    async def assign_permissions(
        self, id: int, org_id: int, permission_keys: list[str]
    ) -> RoleWithPermissions:
        role = await self._repo.get_by_id(id, org_id)
        if not role:
            raise not_found("Role")
        perms = await self._perm_repo.get_by_keys(permission_keys)
        await self._repo.set_permissions(id, [p.id for p in perms])
        role = await self._repo.get_by_id(id, org_id)
        return RoleWithPermissions.model_validate(role)
