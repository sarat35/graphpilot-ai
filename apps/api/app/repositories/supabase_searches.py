from datetime import datetime
from typing import Any
from uuid import UUID

import httpx

from app.schemas.external_listings import SavedExternalListing
from app.schemas.product_search import ProductSearchRequest, RankedProductListing
from app.schemas.searches import SearchSummary


class SupabaseSearchRepository:
    """Persist searches through Supabase PostgREST; no direct database socket is required."""

    def __init__(self, supabase_url: str, secret_key: str) -> None:
        self.base_url = f"{supabase_url.rstrip('/')}/rest/v1"
        self.headers = {
            "apikey": secret_key,
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json",
        }

    async def create(
        self, user_id: UUID, criteria: ProductSearchRequest, results: list[RankedProductListing]
    ) -> SearchSummary:
        search_payload = {
            "user_id": str(user_id),
            "city": criteria.city,
            "min_price_inr": criteria.min_price_inr,
            "max_price_inr": criteria.max_price_inr,
            "brand": criteria.brand,
            "model": criteria.model,
            "fuel_type": criteria.fuel_type.value.title() if criteria.fuel_type else None,
            "max_age_years": criteria.max_age_years,
            "max_kilometres": criteria.max_kilometres,
            "status": "ready" if results else "empty",
        }
        async with self._client() as client:
            created_searches = await self._post(client, "searches", search_payload)
            search = created_searches[0]
            if results:
                payload = [self._result_payload(search["id"], listing) for listing in results]
                await self._post(client, "external_search_results", payload)
        return self._summary(search, len(results))

    async def list_for_member(self, user_id: UUID, limit: int) -> list[SearchSummary]:
        params = {"user_id": f"eq.{user_id}", "order": "created_at.desc", "limit": str(limit)}
        async with self._client() as client:
            searches = await self._get(client, "searches", params)
            summaries = []
            for search in searches:
                results = await self._get(
                    client,
                    "external_search_results",
                    {"search_id": f"eq.{search['id']}", "select": "id"},
                )
                summaries.append(self._summary(search, len(results)))
        return summaries

    async def get_for_member(
        self, search_id: UUID, user_id: UUID
    ) -> tuple[SearchSummary, list[RankedProductListing]] | None:
        async with self._client() as client:
            searches = await self._get(
                client, "searches", {"id": f"eq.{search_id}", "user_id": f"eq.{user_id}"}
            )
            if not searches:
                return None
            rows = await self._get(
                client,
                "external_search_results",
                {"search_id": f"eq.{search_id}", "order": "rank.asc"},
            )
        return self._summary(searches[0], len(rows)), [self._listing(row) for row in rows]

    async def save_external_listing(
        self, user_id: UUID, search_id: UUID, rank: int
    ) -> SavedExternalListing | None:
        async with self._client() as client:
            owned = await self._get(
                client,
                "searches",
                {"id": f"eq.{search_id}", "user_id": f"eq.{user_id}", "select": "id"},
            )
            result = await self._get(
                client,
                "external_search_results",
                {"search_id": f"eq.{search_id}", "rank": f"eq.{rank}"},
            )
            if not owned or not result:
                return None
            saved = await self._post(
                client,
                "saved_external_listings",
                {"user_id": str(user_id), "external_search_result_id": result[0]["id"]},
                prefer="resolution=merge-duplicates,return=representation",
            )
            return self._saved_listing(saved[0], result[0])

    async def get_saved_external_listing(
        self, user_id: UUID, saved_listing_id: UUID, refresh: bool
    ) -> SavedExternalListing | None:
        async with self._client() as client:
            saved = await self._get(
                client,
                "saved_external_listings",
                {"id": f"eq.{saved_listing_id}", "user_id": f"eq.{user_id}"},
            )
            if not saved:
                return None
            result = await self._get(
                client,
                "external_search_results",
                {"id": f"eq.{saved[0]['external_search_result_id']}"},
            )
            if not result:
                return None
            if refresh:
                availability = await self._check_listing_url(result[0]["source_url"])
                if availability != saved[0]["availability"]:
                    saved = await self._patch(
                        client,
                        "saved_external_listings",
                        {"id": f"eq.{saved_listing_id}"},
                        {"availability": availability},
                    )
            return self._saved_listing(saved[0], result[0])

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, headers=self.headers, timeout=20)

    async def _get(
        self, client: httpx.AsyncClient, table: str, params: dict[str, str]
    ) -> list[dict[str, Any]]:
        response = await client.get(f"/{table}", params=params)
        response.raise_for_status()
        return response.json()

    async def _post(
        self,
        client: httpx.AsyncClient,
        table: str,
        payload: Any,
        prefer: str = "return=representation",
    ) -> list[dict[str, Any]]:
        response = await client.post(f"/{table}", json=payload, headers={"Prefer": prefer})
        response.raise_for_status()
        return response.json()

    async def _patch(
        self, client: httpx.AsyncClient, table: str, params: dict[str, str], payload: dict[str, Any]
    ) -> list[dict[str, Any]]:
        response = await client.patch(
            f"/{table}", params=params, json=payload, headers={"Prefer": "return=representation"}
        )
        response.raise_for_status()
        return response.json()

    def _result_payload(self, search_id: str, listing: RankedProductListing) -> dict[str, Any]:
        return {
            "search_id": search_id,
            "rank": listing.rank,
            "title": listing.title,
            "source_url": str(listing.source_url),
            "source_name": listing.source_name,
            "snippet": listing.snippet,
            "raw_result_json": listing.raw_source_data,
            "source_listing_id": listing.vehicle_id,
            "city": listing.city,
            "make": listing.make,
            "model": listing.model,
            "variant": listing.variant,
            "year": listing.year,
            "fuel_type": listing.fuel_type.value.title() if listing.fuel_type else None,
            "transmission": listing.transmission,
            "seller_type": listing.seller_type,
            "price_inr": listing.price_inr,
            "kilometres": listing.kilometres,
            "image_url": str(listing.image_url) if listing.image_url else None,
            "availability": listing.availability.value,
            "match_percentage": listing.match_percentage,
            "match_reasons": listing.match_reasons,
            "unmatched_or_missing_reasons": listing.unmatched_or_missing_reasons,
            "retrieved_at": listing.retrieved_at.isoformat() if listing.retrieved_at else None,
        }

    def _summary(self, row: dict[str, Any], result_count: int) -> SearchSummary:
        return SearchSummary(
            id=row["id"],
            city=row["city"],
            brand=row.get("brand"),
            model=row.get("model"),
            fuel_type=row.get("fuel_type"),
            status=row["status"],
            result_count=result_count,
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
        )

    def _listing(self, row: dict[str, Any]) -> RankedProductListing:
        # The database stores display-friendly fuel values (for example,
        # "Diesel"), while the API schema uses lowercase enum values.
        fuel_type = row.get("fuel_type")
        payload = {
            **row,
            "vehicle_id": row.get("source_listing_id"),
            "fuel_type": fuel_type.lower() if isinstance(fuel_type, str) else fuel_type,
            "raw_source_data": row.get("raw_result_json", {}),
            "retrieved_at": row.get("retrieved_at"),
            "match_reasons": row.get("match_reasons", []),
            "unmatched_or_missing_reasons": row.get("unmatched_or_missing_reasons", []),
        }
        return RankedProductListing(**payload)

    def _saved_listing(self, saved: dict[str, Any], result: dict[str, Any]) -> SavedExternalListing:
        return SavedExternalListing(
            id=saved["id"],
            source_url=result["source_url"],
            title=result["title"],
            source_name=result["source_name"],
            availability=saved["availability"],
            last_checked_at=saved.get("last_checked_at"),
            saved_at=saved["created_at"],
        )

    async def _check_listing_url(self, source_url: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                response = await client.get(source_url, headers={"User-Agent": "BuySeconds/1.0"})
            return "removed" if response.status_code in {404, 410} else "available"
        except httpx.HTTPError:
            return "available"
