from collections.abc import Sequence

import httpx
from pydantic import BaseModel, Field, HttpUrl


class SerperResult(BaseModel):
    vehicle_id: str | None = Field(default=None, max_length=120)
    title: str = Field(min_length=1, max_length=300)
    link: HttpUrl
    snippet: str = Field(default="", max_length=2_000)
    source: str = Field(default="Google")


class SerperSearchPayload(BaseModel):
    organic: list[SerperResult] = Field(default_factory=list, max_length=10)


class GoogleSerperClient:
    def __init__(self, api_key: str, base_url: str) -> None:
        self.api_key = api_key
        self.base_url = base_url

    async def search(self, query: str, limit: int) -> Sequence[SerperResult]:
        if not self.api_key:
            raise RuntimeError("GOOGLE_SERPER_API_KEY is required for live product search")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                self.base_url,
                headers={"X-API-KEY": self.api_key, "Content-Type": "application/json"},
                json={"q": query, "num": min(max(limit * 2, 10), 10)},
            )
        response.raise_for_status()
        # Ask Serper for a wider candidate set.  The ranking graph, rather than
        # the provider's generic web-result order, selects the five listings
        # shown to the customer.
        del limit
        return SerperSearchPayload.model_validate(response.json()).organic


MOCK_SERPER_RESULTS = [
    SerperResult(
        vehicle_id="swift-vxi-amt",
        title="2021 Maruti Suzuki Swift VXI AMT — Bengaluru",
        link="https://example.com/listings/swift-vxi-amt",
        snippet="Certified pre-owned petrol hatchback with 28,500 km. Asking price ₹6,20,000.",
        source="BuySeconds mock marketplace",
    ),
    SerperResult(
        vehicle_id="seltos-gtx-turbo",
        title="2022 Kia Seltos GTX+ Turbo — Bengaluru",
        link="https://example.com/listings/seltos-gtx-turbo",
        snippet="Dealer-certified automatic SUV with 21,300 km. Asking price ₹15,80,000.",
        source="BuySeconds mock marketplace",
    ),
]


class MockGoogleSerperClient:
    async def search(self, query: str, limit: int) -> Sequence[SerperResult]:
        del query
        return MOCK_SERPER_RESULTS[:limit]
