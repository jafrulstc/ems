from typing import Any, Generic, TypeVar
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
    pages: int

async def paginate(
    session: AsyncSession,
    stmt: Any,
    page: int = 1,
    limit: int = 100,
    fetch_all: bool = False
) -> dict[str, Any]:
    """
    Paginate a SQLAlchemy statement and return standard format:
    { items, total, page, limit, pages }
    """
    total = (await session.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    
    if fetch_all or limit == 0:
        items = (await session.execute(stmt)).scalars().all()
        return {
            "items": items,
            "total": total,
            "page": 1,
            "limit": total if total > 0 else 1,
            "pages": 1
        }
        
    offset = (page - 1) * limit
    items = (await session.execute(stmt.offset(offset).limit(limit))).scalars().all()
    pages = max(1, (total + limit - 1) // limit)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }
