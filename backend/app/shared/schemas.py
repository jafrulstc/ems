"""
Shared Pydantic schemas used across all features.

- APIResponse[T]       : standard envelope  { success, message, data }
- PaginatedData[T]     : paginated list payload { items, total, page, size, pages }
- PaginatedResponse[T] : envelope wrapping PaginatedData
"""
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


# ── Standard response envelope ────────────────────────────────────────────────

class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "OK"
    data: Optional[T] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


# ── Paginated payload ─────────────────────────────────────────────────────────

class PaginatedData(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    model_config = ConfigDict(arbitrary_types_allowed=True)


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "OK"
    data: PaginatedData[T]

    model_config = ConfigDict(arbitrary_types_allowed=True)


# ── Convenience constructors ──────────────────────────────────────────────────

def ok(data: T, message: str = "OK") -> APIResponse[T]:
    """Return a successful APIResponse."""
    return APIResponse(success=True, message=message, data=data)


def paginated(
    items: List[T],
    total: int,
    page: int,
    size: int,
    message: str = "OK",
) -> PaginatedResponse[T]:
    """Return a paginated APIResponse."""
    pages = (total + size - 1) // size if size > 0 else 0
    return PaginatedResponse(
        success=True,
        message=message,
        data=PaginatedData(items=items, total=total, page=page, size=size, pages=pages),
    )
