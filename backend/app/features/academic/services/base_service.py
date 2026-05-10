"""Shared service base for academic module."""
from app.shared.exceptions import conflict, not_found
from app.shared.pagination import PaginationParams
from app.shared.schemas import PaginatedData


class BaseAcademicService:
    _repo_class = None
    _schema_read = None
    _resource_name = "Resource"

    def __init__(self, db) -> None:
        self._repo = self._repo_class(db)

    async def list(self, org_id: int, p: PaginationParams) -> PaginatedData:
        items, total = await self._repo.get_many(org_id, p.offset, p.limit)
        return PaginatedData(
            items=[self._schema_read.model_validate(i) for i in items],
            total=total, page=p.page, size=p.size,
            pages=(total + p.size - 1) // p.size if p.size else 0,
        )

    async def get(self, id: int, org_id: int):
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found(self._resource_name)
        return self._schema_read.model_validate(obj)

    async def create(self, org_id: int, payload):
        obj = await self._repo.create(org_id, payload.model_dump())
        return self._schema_read.model_validate(obj)

    async def update(self, id: int, org_id: int, payload):
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found(self._resource_name)
        obj = await self._repo.update(obj, payload.model_dump(exclude_none=True))
        return self._schema_read.model_validate(obj)

    async def delete(self, id: int, org_id: int) -> None:
        obj = await self._repo.get_by_id(id, org_id)
        if not obj:
            raise not_found(self._resource_name)
        await self._repo.soft_delete(obj)
