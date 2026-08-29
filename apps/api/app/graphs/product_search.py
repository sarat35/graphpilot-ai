import re
from datetime import UTC, datetime
from typing import Any, TypedDict
from urllib.parse import urlsplit, urlunsplit

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from app.config.settings import settings
from app.core.logger import logger
from app.integrations.google_serper import SerperResult
from app.schemas.product_search import (
    FuelType,
    ProductListing,
    ProductSearchRequest,
    ProductSearchResponse,
    RankedProductListing,
)


class ProductSearchState(TypedDict, total=False):
    criteria: ProductSearchRequest
    query: str
    candidates: list[ProductListing]
    listings: list[RankedProductListing]
    request_id: str


def build_product_search_query(criteria: ProductSearchRequest, domain: str | None = None) -> str:
    terms: list[str | None] = [criteria.brand, criteria.model, "used car", "Hyderabad"]
    if criteria.fuel_type:
        terms.append(criteria.fuel_type.value)
    if criteria.max_price_inr:
        terms.append(f"under INR {criteria.max_price_inr}")
    if criteria.max_age_years is not None:
        terms.append(f"{datetime.now(UTC).year - criteria.max_age_years} OR newer")
    if criteria.max_kilometres is not None:
        terms.append(f"under {criteria.max_kilometres:,} km")
    if domain:
        terms.append(f"site:{domain}")
    return " ".join(term for term in terms if term)


def canonical_url(url: str) -> str:
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc.lower(), parsed.path.rstrip("/"), "", ""))


def _extract_int(pattern: str, text: str) -> int | None:
    match = re.search(pattern, text, re.IGNORECASE)
    return int(match.group(1).replace(",", "")) if match else None


def to_listing(result: SerperResult, criteria: ProductSearchRequest) -> ProductListing:
    text = f"{result.title} {result.snippet}"
    price = _extract_int(r"(?:₹|rs\.?\s*)\s*([0-9][\d,]*)", text)
    kilometres = _extract_int(r"([\d,]+)\s*(?:km|kms|kilometres)", text)
    year_match = re.search(r"\b(20(?:1\d|2\d))\b", text)
    fuel = next((item for item in FuelType if re.search(rf"\b{item.value}\b", text, re.I)), None)
    return ProductListing(
        vehicle_id=result.vehicle_id,
        title=result.title,
        source_url=result.link,
        source_name=result.source,
        snippet=result.snippet,
        city=criteria.city if criteria.city.lower() in text.lower() else None,
        make=criteria.brand if criteria.brand and criteria.brand.lower() in text.lower() else None,
        model=criteria.model if criteria.model and criteria.model.lower() in text.lower() else None,
        price_inr=price,
        year=int(year_match.group(1)) if year_match else None,
        kilometres=kilometres,
        fuel_type=fuel,
        raw_source_data=result.model_dump(mode="json"),
        retrieved_at=datetime.now(UTC),
    )


def matches_allowed_source(listing: ProductListing) -> bool:
    url = str(listing.source_url).lower()
    return listing.source_name == "BuySeconds mock marketplace" or any(
        domain.strip() in url for domain in settings.product_search_allowed_domains.split(",")
    )


def normalize_and_deduplicate(listings: list[ProductListing], maximum: int) -> list[ProductListing]:
    unique: dict[str, ProductListing] = {}
    for listing in listings:
        if not matches_allowed_source(listing):
            continue
        unique.setdefault(canonical_url(str(listing.source_url)), listing)
        if len(unique) >= maximum:
            break
    return list(unique.values())


def rank_listing(
    listing: ProductListing, criteria: ProductSearchRequest
) -> tuple[int, list[str], list[str]]:
    score, matches, misses = 0, [], []
    if listing.city and listing.city.lower() == criteria.city.lower():
        score += 20
        matches.append("Located in Hyderabad")
    else:
        misses.append("City could not be confirmed")
    if criteria.min_price_inr is None and criteria.max_price_inr is None:
        score += 25
        matches.append("No price limit selected")
    elif listing.price_inr is None:
        misses.append("Price is missing")
    elif (criteria.min_price_inr is None or listing.price_inr >= criteria.min_price_inr) and (
        criteria.max_price_inr is None or listing.price_inr <= criteria.max_price_inr
    ):
        score += 25
        matches.append("Price is within budget")
    else:
        misses.append("Price is outside budget")
    requested_names = [name for name in (criteria.brand, criteria.model) if name]
    text = f"{listing.title} {listing.snippet}".lower()
    if not requested_names:
        score += 25
        matches.append("No brand or model preference selected")
    elif all(name.lower() in text for name in requested_names):
        score += 25
        matches.append("Brand and model match")
    else:
        misses.append("Brand or model does not match")
    if criteria.fuel_type is None:
        score += 10
        matches.append("No fuel preference selected")
    elif listing.fuel_type == criteria.fuel_type:
        score += 10
        matches.append("Fuel type matches")
    else:
        misses.append("Fuel type is missing or does not match")
    if criteria.max_age_years is None:
        score += 10
        matches.append("No maximum age selected")
    elif listing.year is None:
        misses.append("Model year is missing")
    elif listing.year >= datetime.now(UTC).year - criteria.max_age_years:
        score += 10
        matches.append("Vehicle age is within limit")
    else:
        misses.append("Vehicle is older than requested")
    if criteria.max_kilometres is None:
        score += 10
        matches.append("No kilometre limit selected")
    elif listing.kilometres is None:
        misses.append("Kilometres driven is missing")
    elif listing.kilometres <= criteria.max_kilometres:
        score += 10
        matches.append("Kilometres are within limit")
    else:
        misses.append("Kilometres exceed requested limit")
    return score, matches, misses


class ResearchAgent:
    """LangChain tool-using boundary for public marketplace research."""

    def __init__(self, search_client: object, model_name: str) -> None:
        self.search_client = search_client
        self.model_name = model_name
        self.model = (
            ChatOpenAI(model=model_name, api_key=settings.openai_api_key, temperature=0)
            if settings.product_search_mode.lower() == "live"
            else None
        )

    async def _select_domains(
        self, criteria: ProductSearchRequest, domains: list[str]
    ) -> list[str]:
        if self.model is None:
            return domains
        response = await self.model.ainvoke(
            [
                SystemMessage(content=settings.product_search_research_system_prompt),
                HumanMessage(
                    content=(
                        f"Select relevant sources from this exact allowlist: {', '.join(domains)}. "
                        f"Search criteria: {criteria.model_dump_json()}. "
                        "Reply with only selected domains, comma-separated."
                    )
                ),
            ]
        )
        content = str(response.content).lower()
        selected = [domain for domain in domains if domain in content]
        return selected or domains

    async def research(self, criteria: ProductSearchRequest) -> list[ProductListing]:
        @tool("google_serper_product_search")
        async def google_serper_product_search(query: str, limit: int) -> list[dict[str, Any]]:
            """Search an approved marketplace through the configured Google Serper provider."""
            results = await self.search_client.search(query, limit)  # type: ignore[attr-defined]
            return [result.model_dump(mode="json") for result in results]

        collected: list[ProductListing] = []
        domains = [domain.strip() for domain in settings.product_search_allowed_domains.split(",")]
        domains = await self._select_domains(criteria, domains)
        per_source_limit = max(1, settings.product_search_max_candidates // len(domains))
        for domain in domains:
            raw_results = await google_serper_product_search.ainvoke(
                {"query": build_product_search_query(criteria, domain), "limit": per_source_limit}
            )
            collected.extend(
                to_listing(SerperResult.model_validate(item), criteria) for item in raw_results
            )
        return normalize_and_deduplicate(collected, settings.product_search_max_candidates)


class RankingAgent:
    """LangChain agent boundary; score computation is deterministic and auditable."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.model = (
            ChatOpenAI(model=model_name, api_key=settings.openai_api_key, temperature=0)
            if settings.product_search_mode.lower() == "live"
            else None
        )

    async def rank(
        self, candidates: list[ProductListing], criteria: ProductSearchRequest
    ) -> list[RankedProductListing]:
        scored = []
        for listing in candidates:
            score, matches, misses = rank_listing(listing, criteria)
            scored.append((score, listing, matches, misses))
        scored.sort(key=lambda item: item[0], reverse=True)
        ranked = [
            RankedProductListing(
                **listing.model_dump(),
                rank=index,
                match_percentage=score,
                match_reasons=matches,
                unmatched_or_missing_reasons=misses,
            )
            for index, (score, listing, matches, misses) in enumerate(
                scored[: criteria.limit], start=1
            )
        ]
        if self.model is not None:
            # The model may improve human-readable explanations but cannot alter scores or ranks.
            await self.model.ainvoke(
                [
                    SystemMessage(content=settings.product_search_ranking_system_prompt),
                    HumanMessage(content="Review deterministic rankings for factual wording only."),
                ]
            )
        return ranked


class OrchestrationAgent:
    """Shared LangChain model used by LangGraph for run-level orchestration."""

    def __init__(self, model_name: str) -> None:
        self.model = (
            ChatOpenAI(model=model_name, api_key=settings.openai_api_key, temperature=0)
            if settings.product_search_mode.lower() == "live"
            else None
        )

    async def prepare(self, criteria: ProductSearchRequest) -> None:
        if self.model is None:
            return
        await self.model.ainvoke(
            [
                SystemMessage(content="Coordinate the approved used-car search workflow."),
                HumanMessage(
                    content=f"Prepare a Hyderabad search run for: {criteria.model_dump_json()}"
                ),
            ]
        )


def build_product_search_graph(search_client: object, model_name: str):
    research_agent = ResearchAgent(search_client, model_name)
    ranking_agent = RankingAgent(model_name)
    orchestration_agent = OrchestrationAgent(model_name)

    async def validate(state: ProductSearchState) -> dict[str, str]:
        criteria = state["criteria"]
        if criteria.city.casefold() != settings.product_search_allowed_city.casefold():
            raise ValueError(
                f"Only {settings.product_search_allowed_city} searches are currently supported"
            )
        return {"query": build_product_search_query(criteria)}

    async def research(state: ProductSearchState) -> dict[str, list[ProductListing]]:
        await orchestration_agent.prepare(state["criteria"])
        listings = await research_agent.research(state["criteria"])
        logger.bind(request_id=state.get("request_id")).info(
            "product_search_research_complete count={count}", count=len(listings)
        )
        return {"candidates": listings}

    async def rank(state: ProductSearchState) -> dict[str, list[RankedProductListing]]:
        listings = await ranking_agent.rank(state.get("candidates", []), state["criteria"])
        logger.bind(request_id=state.get("request_id")).info(
            "product_search_ranking_complete count={count}", count=len(listings)
        )
        return {"listings": listings}

    graph = StateGraph(ProductSearchState)
    graph.add_node("validate", validate)
    graph.add_node("research_agent", research)
    graph.add_node("ranking_agent", rank)
    graph.add_edge(START, "validate")
    graph.add_edge("validate", "research_agent")
    graph.add_edge("research_agent", "ranking_agent")
    graph.add_edge("ranking_agent", END)
    return graph.compile()


class ProductSearchAgent:
    def __init__(self, search_client: object, model_name: str, result_source: str) -> None:
        self.graph = build_product_search_graph(search_client, model_name)
        self.model_name = model_name
        self.result_source = result_source

    async def search(
        self, criteria: ProductSearchRequest, request_id: str
    ) -> ProductSearchResponse:
        result = await self.graph.ainvoke({"criteria": criteria, "request_id": request_id})
        return ProductSearchResponse(
            query=result["query"],
            results=result.get("listings", []),
            result_source=self.result_source,
            model_name=self.model_name,
            request_id=request_id,
        )
