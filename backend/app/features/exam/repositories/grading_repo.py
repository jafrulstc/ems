"""GradingSystem + GradingRule repositories."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.exam.models import GradingRule, GradingSystem
from app.shared.base_repo import BaseRepo


class GradingSystemRepository(BaseRepo):
    _model = GradingSystem

    async def get_default(self, org_id: int) -> Optional[GradingSystem]:
        r = await self._db.execute(
            select(GradingSystem).where(
                GradingSystem.organization_id == org_id,
                GradingSystem.is_default.is_(True),
                GradingSystem.is_deleted.is_(False),
            )
        )
        return r.scalar_one_or_none()

    async def clear_default(self, org_id: int) -> None:
        from sqlalchemy import update
        await self._db.execute(
            update(GradingSystem)
            .where(GradingSystem.organization_id == org_id)
            .values(is_default=False)
        )

    async def get_rules(self, grading_system_id: int, org_id: int) -> list[GradingRule]:
        r = await self._db.execute(
            select(GradingRule).where(
                GradingRule.grading_system_id == grading_system_id,
                GradingRule.organization_id == org_id,
                GradingRule.is_deleted.is_(False),
            ).order_by(GradingRule.min_marks.desc())
        )
        return list(r.scalars().all())

    async def add_rule(self, org_id: int, grading_system_id: int, data: dict) -> GradingRule:
        obj = GradingRule(organization_id=org_id, grading_system_id=grading_system_id, **data)
        self._db.add(obj)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def resolve_grade(
        self, grading_system_id: int, org_id: int, percentage: float
    ) -> Optional[GradingRule]:
        """Find the matching grade band for a given percentage."""
        rules = await self.get_rules(grading_system_id, org_id)
        for rule in rules:
            if float(rule.min_marks) <= percentage <= float(rule.max_marks):
                return rule
        # Fallback: lowest rule
        return rules[-1] if rules else None
