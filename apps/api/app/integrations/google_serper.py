import asyncio
from collections.abc import Sequence
from urllib.parse import urlparse

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


class LangChainGoogleSerperClient:
    """Adapter that keeps LangChain's Serper wrappers behind our typed boundary."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def search(self, query: str, limit: int) -> Sequence[SerperResult]:
        if not self.api_key:
            raise RuntimeError("GOOGLE_SERPER_API_KEY is required for live product search")
        try:
            from langchain_community.tools.google_serper import GoogleSerperRun
            from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
        except (
            ImportError
        ) as error:  # pragma: no cover - dependency installation is deployment-specific
            raise RuntimeError("langchain-community is required for live product search") from error

        wrapper = GoogleSerperAPIWrapper(serper_api_key=self.api_key, k=min(limit, 10))
        run_tool = GoogleSerperRun(api_wrapper=wrapper)
        # GoogleSerperRun is the tool-facing middleware invocation.  The wrapper
        # returns the structured organic payload used for evidence and persistence.
        await asyncio.to_thread(run_tool.invoke, query)
        payload = await asyncio.to_thread(wrapper.results, query)
        organic = payload.get("organic", []) if isinstance(payload, dict) else []
        results = []
        for item in organic[:limit]:
            link = item.get("link")
            title = item.get("title")
            if not link or not title:
                continue
            results.append(
                SerperResult(
                    vehicle_id=item.get("position") and str(item["position"]),
                    title=title,
                    link=link,
                    snippet=item.get("snippet", ""),
                    source=urlparse(link).netloc,
                )
            )
        return results


MOCK_SERPER_RESULTS = [
    SerperResult(
        vehicle_id="swift-vxi-amt",
        title="2021 Maruti Suzuki Swift VXI AMT — Hyderabad",
        link="https://example.com/listings/swift-vxi-amt",
        snippet="Certified pre-owned petrol hatchback with 28,500 km. Asking price ₹6,20,000.",
        source="BuySeconds mock marketplace",
    ),
    SerperResult(
        vehicle_id="seltos-gtx-turbo",
        title="2022 Kia Seltos GTX+ Turbo — Hyderabad",
        link="https://example.com/listings/seltos-gtx-turbo",
        snippet="Dealer-certified automatic SUV with 21,300 km. Asking price ₹15,80,000.",
        source="BuySeconds mock marketplace",
    ),
]


class MockGoogleSerperClient:
    async def search(self, query: str, limit: int) -> Sequence[SerperResult]:
        del query
        return MOCK_SERPER_RESULTS[:limit]
