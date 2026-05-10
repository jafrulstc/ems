"""
Pagination helpers for query parameters and result slicing.
"""
from math import ceil
from typing import Optional

from fastapi import Query
from pydantic import BaseModel, field_validator


class PaginationParams(BaseModel):
    """Validated pagination query parameters — inject via Depends(pagination_params)."""

    page: int = 1
    size: int = 20

    @field_validator("page")
    @classmethod
    def page_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("page must be ≥ 1")
        return v

    @field_validator("size")
    @classmethod
    def size_must_be_in_range(cls, v: int) -> int:
        if not (1 <= v <= 200):
            raise ValueError("size must be between 1 and 200")
        return v

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        return self.size


def pagination_params(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(default=20, ge=1, le=200, description="Items per page"),
) -> PaginationParams:
    """
    FastAPI dependency factory for pagination query params.

    Usage:
        @router.get("/items")
        async def list_items(p: PaginationParams = Depends(pagination_params)):
            ...
    """
    return PaginationParams(page=page, size=size)
