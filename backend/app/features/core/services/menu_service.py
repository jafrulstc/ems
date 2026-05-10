"""Menu service — business logic layer."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.core.repositories.menu_repo import MenuRepository
from app.features.core.schemas import MenuCreate, MenuRead, MenuUpdate
from app.shared.exceptions import not_found


class MenuService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = MenuRepository(db)

    async def get_tree(self, org_id: int) -> list[MenuRead]:
        """Return nested menu tree for sidebar rendering."""
        roots = await self._repo.get_tree(org_id)
        return [MenuRead.model_validate(r) for r in roots]

    async def get_flat(self, org_id: int) -> list[MenuRead]:
        items = await self._repo.get_all_flat(org_id)
        return [MenuRead.model_validate(i) for i in items]

    async def create(self, org_id: int, payload: MenuCreate) -> MenuRead:
        # Validate parent belongs to same org
        if payload.parent_id is not None:
            parent = await self._repo.get_by_id(payload.parent_id, org_id)
            if not parent:
                raise not_found("Parent menu item")
        obj = await self._repo.create(org_id, payload.model_dump())
        return MenuRead.model_validate(obj)

    async def update(self, id: int, org_id: int, payload: MenuUpdate) -> MenuRead:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found("Menu item")
        data = payload.model_dump(exclude_unset=True)
        obj = await self._repo.update(obj, data)
        return MenuRead.model_validate(obj)

    async def delete(self, id: int, org_id: int) -> None:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found("Menu item")
        await self._repo.soft_delete(obj)
