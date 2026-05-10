"""User management service."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.repositories.user_repo import UserRepository
from app.features.auth.schemas import UserCreate, UserRead, UserUpdate
from app.features.auth.security import hash_password
from app.shared.exceptions import conflict, not_found
from app.shared.pagination import PaginationParams
from app.shared.schemas import PaginatedData


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = UserRepository(db)

    async def list(self, org_id: int, p: PaginationParams) -> PaginatedData[UserRead]:
        items, total = await self._repo.get_many(org_id, p.offset, p.limit)
        return PaginatedData(
            items=[UserRead.model_validate(u) for u in items],
            total=total, page=p.page, size=p.size,
            pages=(total + p.size - 1) // p.size if p.size else 0,
        )

    async def get(self, id: int, org_id: int) -> UserRead:
        user = await self._repo.get_by_id(id, org_id)
        if not user:
            raise not_found("User")
        return UserRead.model_validate(user)

    async def create(self, org_id: int, payload: UserCreate) -> UserRead:
        existing = await self._repo.get_by_email(payload.email, org_id)
        if existing:
            raise conflict("A user with this email already exists.")
        data = payload.model_dump(exclude={"password"})
        data["hashed_password"] = hash_password(payload.password)
        user = await self._repo.create(org_id, data)
        return UserRead.model_validate(user)

    async def update(self, id: int, org_id: int, payload: UserUpdate) -> UserRead:
        user = await self._repo.get_by_id(id, org_id)
        if not user:
            raise not_found("User")
        data = payload.model_dump(exclude_none=True, exclude={"password"})
        if payload.password:
            data["hashed_password"] = hash_password(payload.password)
        user = await self._repo.update(user, data)
        return UserRead.model_validate(user)

    async def delete(self, id: int, org_id: int) -> None:
        user = await self._repo.get_by_id(id, org_id)
        if not user:
            raise not_found("User")
        await self._repo.soft_delete(user)

    async def set_roles(self, id: int, org_id: int, role_ids: list[int]) -> UserRead:
        user = await self._repo.get_by_id(id, org_id)
        if not user:
            raise not_found("User")
        await self._repo.set_roles(id, role_ids)
        return await self.get(id, org_id)
