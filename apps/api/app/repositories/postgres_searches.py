import json
from uuid import UUID

import asyncpg
import httpx

from app.schemas.external_listings import SavedExternalListing
from app.schemas.product_search import ProductSearchRequest, RankedProductListing
from app.schemas.searches import SearchSummary


class PostgresSearchRepository:
    """Supabase/Postgres persistence for completed external product searches."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    async def create(
        self, user_id: UUID, criteria: ProductSearchRequest, results: list[RankedProductListing]
    ) -> SearchSummary:
        connection = await asyncpg.connect(self.database_url)
        try:
            async with connection.transaction():
                search = await connection.fetchrow(
                    """
                    insert into public.searches
                        (user_id, city, min_price_inr, max_price_inr, brand, model, fuel_type,
                         max_age_years, max_kilometres, status)
                    values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    returning id, city, brand, model, fuel_type, status, created_at
                    """,
                    user_id,
                    criteria.city,
                    criteria.min_price_inr,
                    criteria.max_price_inr,
                    criteria.brand,
                    criteria.model,
                    criteria.fuel_type.value.title() if criteria.fuel_type else None,
                    criteria.max_age_years,
                    criteria.max_kilometres,
                    "ready" if results else "empty",
                )
                for listing in results:
                    await connection.execute(
                        """
                        insert into public.external_search_results
                            (search_id, rank, title, source_url, source_name, snippet,
                             raw_result_json, source_listing_id, city, make, model, variant,
                             year, fuel_type, transmission, seller_type, price_inr, kilometres,
                             image_url, availability, match_percentage, match_reasons,
                             unmatched_or_missing_reasons, retrieved_at)
                        values ($1, $2, $3, $4, $5, $6, $7::jsonb, $8, $9, $10, $11, $12, $13, $14,
                                $15, $16, $17, $18, $19, $20, $21, $22::jsonb, $23::jsonb, $24)
                        """,
                        search["id"],
                        listing.rank,
                        listing.title,
                        str(listing.source_url),
                        listing.source_name,
                        listing.snippet,
                        json.dumps(listing.raw_source_data),
                        listing.vehicle_id,
                        listing.city,
                        listing.make,
                        listing.model,
                        listing.variant,
                        listing.year,
                        listing.fuel_type.value.title() if listing.fuel_type else None,
                        listing.transmission,
                        listing.seller_type,
                        listing.price_inr,
                        listing.kilometres,
                        str(listing.image_url) if listing.image_url else None,
                        listing.availability.value,
                        listing.match_percentage,
                        json.dumps(listing.match_reasons),
                        json.dumps(listing.unmatched_or_missing_reasons),
                        listing.retrieved_at,
                    )
            return SearchSummary(
                id=search["id"],
                city=search["city"],
                brand=search["brand"],
                model=search["model"],
                fuel_type=search["fuel_type"],
                status=search["status"],
                result_count=len(results),
                created_at=search["created_at"],
            )
        finally:
            await connection.close()

    async def list_for_member(self, user_id: UUID, limit: int) -> list[SearchSummary]:
        connection = await asyncpg.connect(self.database_url)
        try:
            rows = await connection.fetch(
                """
                select s.id, s.city, s.brand, s.model, s.fuel_type, s.status, s.created_at,
                       count(r.id)::integer as result_count
                from public.searches s
                left join public.external_search_results r on r.search_id = s.id
                where s.user_id = $1 group by s.id order by s.created_at desc limit $2
                """,
                user_id,
                limit,
            )
            return [SearchSummary(**dict(row)) for row in rows]
        finally:
            await connection.close()

    async def get_for_member(
        self, search_id: UUID, user_id: UUID
    ) -> tuple[SearchSummary, list[RankedProductListing]] | None:
        connection = await asyncpg.connect(self.database_url)
        try:
            search = await connection.fetchrow(
                """
                select s.id, s.city, s.brand, s.model, s.fuel_type, s.status, s.created_at,
                       count(r.id)::integer as result_count
                from public.searches s
                left join public.external_search_results r on r.search_id = s.id
                where s.id = $1 and s.user_id = $2 group by s.id
                """,
                search_id,
                user_id,
            )
            if search is None:
                return None
            rows = await connection.fetch(
                """
                select source_listing_id as vehicle_id, title, source_url, source_name, snippet,
                       city, make, model, variant, price_inr, year, kilometres,
                       lower(fuel_type) as fuel_type, transmission, seller_type, image_url,
                       availability, raw_result_json as raw_source_data, retrieved_at, rank,
                       match_percentage, match_reasons, unmatched_or_missing_reasons
                from public.external_search_results where search_id = $1 order by rank
                """,
                search_id,
            )
            return SearchSummary(**dict(search)), [
                RankedProductListing(**dict(row)) for row in rows
            ]
        finally:
            await connection.close()

    async def save_external_listing(
        self, user_id: UUID, search_id: UUID, rank: int
    ) -> SavedExternalListing | None:
        connection = await asyncpg.connect(self.database_url)
        try:
            row = await connection.fetchrow(
                """
                insert into public.saved_external_listings (user_id, external_search_result_id)
                select $1, result.id
                from public.external_search_results result
                join public.searches search on search.id = result.search_id
                where result.search_id = $2 and result.rank = $3 and search.user_id = $1
                on conflict (user_id, external_search_result_id) do update
                set availability = public.saved_external_listings.availability
                returning id, availability, last_checked_at, created_at, external_search_result_id
                """,
                user_id,
                search_id,
                rank,
            )
            if row is None:
                return None
            return await self._saved_listing(connection, row["id"], user_id)
        finally:
            await connection.close()

    async def get_saved_external_listing(
        self, user_id: UUID, saved_listing_id: UUID, refresh: bool
    ) -> SavedExternalListing | None:
        connection = await asyncpg.connect(self.database_url)
        try:
            saved = await self._saved_listing(connection, saved_listing_id, user_id)
            if saved is None or not refresh:
                return saved
            availability = await self._check_listing_url(str(saved.source_url))
            await connection.execute(
                """
                update public.saved_external_listings
                set availability = $1, last_checked_at = timezone('utc', now())
                where id = $2 and user_id = $3
                """,
                availability,
                saved_listing_id,
                user_id,
            )
            return await self._saved_listing(connection, saved_listing_id, user_id)
        finally:
            await connection.close()

    async def _saved_listing(
        self, connection: asyncpg.Connection, saved_listing_id: UUID, user_id: UUID
    ) -> SavedExternalListing | None:
        row = await connection.fetchrow(
            """
            select saved.id, result.source_url, result.title, result.source_name,
                   saved.availability, saved.last_checked_at, saved.created_at as saved_at
            from public.saved_external_listings saved
            join public.external_search_results result
              on result.id = saved.external_search_result_id
            where saved.id = $1 and saved.user_id = $2
            """,
            saved_listing_id,
            user_id,
        )
        return SavedExternalListing(**dict(row)) if row else None

    async def _check_listing_url(self, source_url: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                response = await client.get(source_url, headers={"User-Agent": "BuySeconds/1.0"})
            return "removed" if response.status_code in {404, 410} else "available"
        except httpx.HTTPError:
            # A transient source failure must not falsely remove a customer's saved listing.
            return "available"
