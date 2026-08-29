from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.schemas.product_search import ProductSearchRequest, RankedProductListing
from app.schemas.searches import SearchSummary


@dataclass(frozen=True)
class MockSearchRecord:
    id: UUID
    user_id: UUID
    criteria: ProductSearchRequest
    results: list[RankedProductListing]
    created_at: datetime

    def summary(self) -> SearchSummary:
        return SearchSummary(
            id=self.id,
            city=self.criteria.city,
            brand=self.criteria.brand,
            model=self.criteria.model,
            fuel_type=self.criteria.fuel_type.value if self.criteria.fuel_type else None,
            status="ready" if self.results else "empty",
            result_count=len(self.results),
            created_at=self.created_at,
        )


class MockSearchRepository:
    """In-memory Warehouse substitute used only while PRODUCT_SEARCH_MODE=mock."""

    def __init__(self) -> None:
        self._records: dict[UUID, MockSearchRecord] = {}

    async def create(
        self, user_id: UUID, criteria: ProductSearchRequest, results: list[RankedProductListing]
    ) -> MockSearchRecord:
        record = MockSearchRecord(
            id=uuid4(),
            user_id=user_id,
            criteria=criteria,
            results=results,
            created_at=datetime.now(UTC),
        )
        self._records[record.id] = record
        return record

    async def list_for_member(self, user_id: UUID, limit: int) -> list[MockSearchRecord]:
        records = [record for record in self._records.values() if record.user_id == user_id]
        return sorted(records, key=lambda record: record.created_at, reverse=True)[:limit]

    async def get_for_member(self, search_id: UUID, user_id: UUID) -> MockSearchRecord | None:
        record = self._records.get(search_id)
        return record if record and record.user_id == user_id else None

    def clear(self) -> None:
        self._records.clear()
