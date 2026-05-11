"""Tests for the shared kernel — interface-level, no internal state inspection.

Each test asserts observable behavior through the public interface of the
module under test.  Internal implementation details are not tested.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.shared.clock import FixedClock, SystemClock
from app.shared.errors import (
    AuthorizationError,
    ConflictError,
    DomainError,
    InvariantError,
    NotFoundError,
)
from app.shared.errors import (
    ValidationError as DomainValidationError,
)
from app.shared.ids import (
    BuildingId,
    FacilityId,
    new_id,
)
from app.shared.pagination import Page, PageParams
from app.shared.result import Err, Ok

# ── errors ─────────────────────────────────────────────────────────────────────


class TestDomainErrors:
    def test_domain_error_stores_message(self) -> None:
        err = DomainError("something went wrong")
        assert err.message == "something went wrong"
        assert str(err) == "something went wrong"

    def test_not_found_is_domain_error(self) -> None:
        err = NotFoundError("building not found")
        assert isinstance(err, DomainError)
        assert err.message == "building not found"

    def test_conflict_is_domain_error(self) -> None:
        assert isinstance(ConflictError("dup"), DomainError)

    def test_authorization_is_domain_error(self) -> None:
        assert isinstance(AuthorizationError("denied"), DomainError)

    def test_validation_is_domain_error(self) -> None:
        assert isinstance(DomainValidationError("bad input"), DomainError)

    def test_invariant_is_domain_error(self) -> None:
        assert isinstance(InvariantError("broken"), DomainError)

    def test_can_raise_and_catch_as_base(self) -> None:
        with pytest.raises(DomainError, match="not found"):
            raise NotFoundError("not found")


# ── result ─────────────────────────────────────────────────────────────────────


class TestResult:
    def test_ok_is_ok(self) -> None:
        result: Ok[int] = Ok(42)
        assert result.is_ok()
        assert not result.is_err()

    def test_ok_unwrap_returns_value(self) -> None:
        assert Ok("hello").unwrap() == "hello"

    def test_err_is_err(self) -> None:
        result: Err[NotFoundError] = Err(NotFoundError("x"))
        assert result.is_err()
        assert not result.is_ok()

    def test_err_unwrap_raises(self) -> None:
        err = NotFoundError("missing")
        with pytest.raises(NotFoundError, match="missing"):
            Err(err).unwrap()

    def test_match_ok(self) -> None:
        result: Ok[int] | Err[NotFoundError] = Ok(99)
        match result:
            case Ok(value=v):
                assert v == 99
            case Err():
                pytest.fail("expected Ok")

    def test_match_err(self) -> None:
        result: Ok[int] | Err[NotFoundError] = Err(NotFoundError("gone"))
        match result:
            case Ok():
                pytest.fail("expected Err")
            case Err(error=e):
                assert isinstance(e, NotFoundError)


# ── ids ────────────────────────────────────────────────────────────────────────


class TestIds:
    def test_new_id_returns_uuid(self) -> None:
        fid = new_id(FacilityId)
        assert isinstance(fid, uuid.UUID)

    def test_new_ids_are_unique(self) -> None:
        a = new_id(FacilityId)
        b = new_id(FacilityId)
        assert a != b

    def test_different_id_types_are_distinct_at_runtime(self) -> None:
        fid = new_id(FacilityId)
        bid = new_id(BuildingId)
        # NewType is identity at runtime — both are uuid.UUID instances
        assert isinstance(fid, uuid.UUID)
        assert isinstance(bid, uuid.UUID)
        # but they should be different values
        assert fid != bid


# ── clock ──────────────────────────────────────────────────────────────────────


class TestClock:
    def test_system_clock_returns_utc_datetime(self) -> None:
        now = SystemClock().now()
        assert now.tzinfo is not None
        assert now.tzinfo == UTC

    def test_fixed_clock_returns_fixed_value(self) -> None:
        fixed = datetime(2024, 6, 1, 12, 0, 0, tzinfo=UTC)
        clock = FixedClock(fixed)
        assert clock.now() == fixed
        assert clock.now() == fixed  # idempotent

    def test_system_clock_advances(self) -> None:
        clock = SystemClock()
        t1 = clock.now()
        t2 = clock.now()
        assert t2 >= t1


# ── pagination ─────────────────────────────────────────────────────────────────


class TestPageParams:
    def test_default_params(self) -> None:
        p = PageParams()
        assert p.page == 1
        assert p.size == 20
        assert p.offset == 0
        assert p.limit == 20

    def test_offset_calculation(self) -> None:
        p = PageParams(page=3, size=10)
        assert p.offset == 20
        assert p.limit == 10

    def test_page_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            PageParams(page=0)

    def test_size_capped_at_100(self) -> None:
        with pytest.raises(ValidationError):
            PageParams(size=101)


class TestPage:
    def test_basic_page(self) -> None:
        params = PageParams(page=1, size=5)
        page: Page[int] = Page.of(items=[1, 2, 3], total=3, params=params)
        assert page.items == [1, 2, 3]
        assert page.total == 3
        assert page.pages == 1
        assert not page.has_next
        assert not page.has_prev

    def test_multi_page(self) -> None:
        params = PageParams(page=2, size=5)
        page: Page[int] = Page.of(items=list(range(5)), total=13, params=params)
        assert page.pages == 3
        assert page.has_next
        assert page.has_prev

    def test_empty_page(self) -> None:
        params = PageParams(page=1, size=10)
        page: Page[int] = Page.of(items=[], total=0, params=params)
        assert page.pages == 0
        assert not page.has_next
        assert not page.has_prev

    def test_items_exceeding_size_raises(self) -> None:
        with pytest.raises(ValidationError):
            Page[int](items=list(range(11)), total=11, page=1, size=10)
