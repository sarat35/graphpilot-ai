from uuid import UUID

from fastapi import HTTPException, status

from app.repositories.mock_searches import MockSearchRepository
from app.schemas.product_search import ProductSearchRequest
from app.schemas.searches import CreateSearchResponse, SearchResultsResponse, SearchSummary
from app.services.product_search import search_products

mock_search_repository = MockSearchRepository()


async def create_search(
    user_id: UUID, criteria: ProductSearchRequest, request_id: str
) -> CreateSearchResponse:
    product_response = await search_products(criteria, request_id)
    record = await mock_search_repository.create(user_id, criteria, product_response.results)
    return CreateSearchResponse(search=record.summary())


async def list_searches(user_id: UUID, limit: int) -> list[SearchSummary]:
    records = await mock_search_repository.list_for_member(user_id, limit)
    return [record.summary() for record in records]


async def get_search_results(user_id: UUID, search_id: UUID) -> SearchResultsResponse:
    record = await mock_search_repository.get_for_member(search_id, user_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search not found")
    return SearchResultsResponse(search=record.summary(), results=record.results)
