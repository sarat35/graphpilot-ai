from uuid import UUID

from fastapi import HTTPException, status

from app.config.settings import settings
from app.repositories.mock_searches import MockSearchRepository
from app.repositories.postgres_searches import PostgresSearchRepository
from app.repositories.supabase_searches import SupabaseSearchRepository
from app.schemas.product_search import ProductSearchRequest
from app.schemas.searches import CreateSearchResponse, SearchResultsResponse, SearchSummary
from app.services.product_search import search_products

mock_search_repository = MockSearchRepository()


def _repository() -> MockSearchRepository | PostgresSearchRepository | SupabaseSearchRepository:
    if settings.product_search_mode.lower() == "mock":
        return mock_search_repository
    if settings.supabase_url and (
        settings.supabase_secret_key or settings.supabase_service_role_key
    ):
        return SupabaseSearchRepository(
            settings.supabase_url,
            settings.supabase_secret_key or settings.supabase_service_role_key,
        )
    return PostgresSearchRepository(settings.database_url)


async def create_search(
    user_id: UUID, criteria: ProductSearchRequest, request_id: str
) -> CreateSearchResponse:
    product_response = await search_products(criteria, request_id)
    record = await _repository().create(user_id, criteria, product_response.results)
    return CreateSearchResponse(search=record.summary() if hasattr(record, "summary") else record)


async def list_searches(user_id: UUID, limit: int) -> list[SearchSummary]:
    records = await _repository().list_for_member(user_id, limit)
    return [record.summary() if hasattr(record, "summary") else record for record in records]


async def get_search_results(user_id: UUID, search_id: UUID) -> SearchResultsResponse:
    record = await _repository().get_for_member(search_id, user_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search not found")
    if isinstance(record, tuple):
        search, results = record
        return SearchResultsResponse(search=search, results=results)
    return SearchResultsResponse(search=record.summary(), results=record.results)
