"""Typed pagination primitives used across all query interfaces.

``PageParams`` carries caller-supplied pagination intent.
``Page[T]`` is the generic paginated response returned by query use-cases.

Both are immutable Pydantic models so they serialise correctly at the
presentation layer without additional mapping.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

_MAX_PAGE_SIZE = 100
_DEFAULT_PAGE_SIZE = 20


class PageParams(BaseModel):
    """Pagination request parameters validated at the presentation boundary."""

    model_config = ConfigDict(frozen=True)

    page: int = Field(default=1, ge=1, description="1-based page number.")
    size: int = Field(
        default=_DEFAULT_PAGE_SIZE,
        ge=1,
        le=_MAX_PAGE_SIZE,
        description=f"Items per page (max {_MAX_PAGE_SIZE}).",
    )

    @property
    def offset(self) -> int:
        """Zero-based row offset for SQL ``OFFSET`` clause."""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Row limit for SQL ``LIMIT`` clause — same as ``size``."""
        return self.size


class Page[T](BaseModel):
    """Generic paginated response.

    ``items`` contains at most ``params.size`` elements.
    ``total`` is the full unfiltered count (used for client-side page math).
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    items: list[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    size: int = Field(ge=1)

    @model_validator(mode="after")
    def _items_fit_page(self) -> Page[T]:
        if len(self.items) > self.size:
            raise ValueError(f"items length {len(self.items)} exceeds page size {self.size}")
        return self

    @property
    def pages(self) -> int:
        """Total number of pages."""
        if self.total == 0:
            return 0
        return (self.total + self.size - 1) // self.size

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @classmethod
    def of(cls, items: list[T], total: int, params: PageParams) -> Page[T]:
        """Construct a ``Page`` from a result list, total count, and params."""
        return cls(items=items, total=total, page=params.page, size=params.size)
