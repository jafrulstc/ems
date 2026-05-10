"""Grading system service — handles rules inline on create and default switching."""
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.exam.repositories.grading_repo import GradingSystemRepository
from app.features.exam.schemas import (
    GradingRuleCreate, GradingRuleRead,
    GradingSystemCreate, GradingSystemRead, GradingSystemUpdate,
)
from app.shared.exceptions import not_found
from app.shared.pagination import PaginationParams
from app.shared.schemas import PaginatedData


class GradingService:
    def __init__(self, db: AsyncSession):
        self._repo = GradingSystemRepository(db)

    async def list(self, org_id: int, p: PaginationParams) -> PaginatedData[GradingSystemRead]:
        items, total = await self._repo.get_many(org_id, p.offset, p.limit)
        results = []
        for gs in items:
            rules = await self._repo.get_rules(gs.id, org_id)
            read = GradingSystemRead.model_validate(gs)
            read.rules = [GradingRuleRead.model_validate(r) for r in rules]
            results.append(read)
        return PaginatedData(items=results, total=total, page=p.page, size=p.size,
                             pages=(total + p.size - 1) // p.size if p.size else 0)

    async def get(self, id: int, org_id: int) -> GradingSystemRead:
        gs = await self._repo.get_by_id(id, org_id)
        if not gs: raise not_found("GradingSystem")
        rules = await self._repo.get_rules(id, org_id)
        read = GradingSystemRead.model_validate(gs)
        read.rules = [GradingRuleRead.model_validate(r) for r in rules]
        return read

    async def create(self, org_id: int, payload: GradingSystemCreate) -> GradingSystemRead:
        if payload.is_default:
            await self._repo.clear_default(org_id)
        gs = await self._repo.create(org_id, {"name": payload.name, "is_default": payload.is_default})
        for rule in payload.rules:
            await self._repo.add_rule(org_id, gs.id, rule.model_dump())
        return await self.get(gs.id, org_id)

    async def update(self, id: int, org_id: int, payload: GradingSystemUpdate) -> GradingSystemRead:
        gs = await self._repo.get_by_id(id, org_id)
        if not gs: raise not_found("GradingSystem")
        if payload.is_default:
            await self._repo.clear_default(org_id)
        await self._repo.update(gs, payload.model_dump(exclude_none=True))
        return await self.get(id, org_id)

    async def delete(self, id: int, org_id: int) -> None:
        gs = await self._repo.get_by_id(id, org_id)
        if not gs: raise not_found("GradingSystem")
        await self._repo.soft_delete(gs)

    async def add_rule(self, id: int, org_id: int, payload: GradingRuleCreate) -> GradingRuleRead:
        gs = await self._repo.get_by_id(id, org_id)
        if not gs: raise not_found("GradingSystem")
        rule = await self._repo.add_rule(org_id, id, payload.model_dump())
        return GradingRuleRead.model_validate(rule)
