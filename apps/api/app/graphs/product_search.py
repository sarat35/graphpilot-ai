import re
from datetime import UTC, datetime
from typing import TypedDict

from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph

from app.integrations.google_serper import SerperResult
from app.schemas.product_search import ProductListing, ProductSearchRequest, ProductSearchResponse


class ProductSearchState(TypedDict, total=False):
    criteria: ProductSearchRequest
    query: str
    listings: list[ProductListing]


def build_product_search_query(criteria: ProductSearchRequest) -> str:
    terms = [criteria.brand, criteria.model, "used"]
    if criteria.fuel_type:
        terms.append(criteria.fuel_type.value)
    terms.extend(
        [
            "cars for sale in",
            criteria.city,
        ]
    )
    if criteria.max_price_inr:
        terms.append(f"under INR {criteria.max_price_inr}")
    if criteria.max_age_years is not None:
        earliest_year = datetime.now(UTC).year - criteria.max_age_years
        terms.append(f"{earliest_year} OR newer")
    if criteria.max_kilometres is not None:
        terms.append(f"under {criteria.max_kilometres:,} km")
    terms.append("individual listing")
    return " ".join(term for term in terms if term)


def to_listing(result: SerperResult) -> ProductListing:
    return ProductListing(
        vehicle_id=result.vehicle_id,
        title=result.title,
        source_url=result.link,
        source_name=result.source,
        snippet=result.snippet,
    )


def value_score(listing: ProductListing, criteria: ProductSearchRequest) -> int:
    text = f"{listing.title} {listing.snippet}".lower()
    score = 0
    if criteria.city.lower() in text:
        score += 120
    if criteria.brand and criteria.brand.lower() in text:
        score += 80
    if criteria.model and criteria.model.lower() in text:
        score += 120
    if criteria.fuel_type and criteria.fuel_type.value in text:
        score += 50
    if "₹" in text or "rs" in text or "price" in text:
        score += 20
    if re.search(r"\b20(?:1\d|2\d)\b", text):
        score += 20
    if re.search(r"\b[\d,]+\s*(?:km|kms|kilometres)\b", text):
        score += 20
    return score


def is_vehicle_marketplace(listing: ProductListing) -> bool:
    return listing.source_name == "BuySeconds mock marketplace" or any(
        domain in str(listing.source_url).lower()
        for domain in ["cars24.com", "carwale.com", "cartrade.com", "spinny.com", "olx.in"]
    )


def is_direct_listing(listing: ProductListing) -> bool:
    text = f"{listing.title} {listing.snippet}".lower()
    category_phrases = ["used cars in", "used cars for sale", "second hand cars"]
    has_year = bool(re.search(r"\b20(?:1\d|2\d)\b", text))
    has_price = "₹" in text or "rs." in text or "rs " in text or "price" in text
    return not any(phrase in text for phrase in category_phrases) and has_year and has_price


def build_product_search_graph(search_client: object):
    @tool("google_serper_product_search")
    async def google_serper_product_search(query: str, limit: int) -> list[dict[str, str]]:
        """Retrieve current product listings from the configured Google Serper provider."""
        results = await search_client.search(query, limit)  # type: ignore[attr-defined]
        return [result.model_dump(mode="json") for result in results]

    async def build_query(state: ProductSearchState) -> dict[str, str]:
        return {"query": build_product_search_query(state["criteria"])}

    async def retrieve_listings(state: ProductSearchState) -> dict[str, list[ProductListing]]:
        raw_results = await google_serper_product_search.ainvoke(
            {"query": state["query"], "limit": state["criteria"].limit}
        )
        listings = [to_listing(SerperResult.model_validate(item)) for item in raw_results]
        city_matches = [
            listing
            for listing in listings
            if state["criteria"].city.lower() in f"{listing.title} {listing.snippet}".lower()
            and is_vehicle_marketplace(listing)
            and is_direct_listing(listing)
        ]
        # Google snippets often omit a year or price even when the linked page
        # is a vehicle listing.  Prefer fully evidenced listings, but do not
        # reject a city-specific product result merely because one snippet field
        # was omitted.  Generic category/search pages remain excluded.
        if not city_matches:
            city_matches = [
                listing
                for listing in listings
                if state["criteria"].city.lower()
                in f"{listing.title} {listing.snippet}".lower()
                and is_vehicle_marketplace(listing)
                and not any(
                    phrase in f"{listing.title} {listing.snippet}".lower()
                    for phrase in ["used cars in", "used cars for sale", "second hand cars"]
                )
            ]
        ranked = sorted(
            city_matches, key=lambda listing: value_score(listing, state["criteria"]), reverse=True
        )
        return {"listings": ranked[: state["criteria"].limit]}

    graph = StateGraph(ProductSearchState)
    graph.add_node("build_query", build_query)
    graph.add_node("google_serper_tool", retrieve_listings)
    graph.add_edge(START, "build_query")
    graph.add_edge("build_query", "google_serper_tool")
    graph.add_edge("google_serper_tool", END)
    return graph.compile()


class ProductSearchAgent:
    def __init__(self, search_client: object, model_name: str, result_source: str) -> None:
        self.graph = build_product_search_graph(search_client)
        self.model_name = model_name
        self.result_source = result_source

    async def search(
        self, criteria: ProductSearchRequest, request_id: str
    ) -> ProductSearchResponse:
        result = await self.graph.ainvoke({"criteria": criteria})
        return ProductSearchResponse(
            query=result["query"],
            results=result.get("listings", []),
            result_source=self.result_source,
            model_name=self.model_name,
            request_id=request_id,
        )
