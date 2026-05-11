from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import SpsControllerSystemTypeId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class GetSpsControllerSystemTypeQuery:
    system_type_id: SpsControllerSystemTypeId


@dataclass(frozen=True, slots=True)
class ListSpsControllerSystemTypesQuery:
    page: PageParams
