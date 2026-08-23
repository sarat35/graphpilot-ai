from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.auth.dependencies import CurrentMember, get_current_member
from app.schemas.product_search import ProductSearchRequest
from app.schemas.searches import CreateSearchResponse, SearchResultsResponse, SearchSummary
from app.services.searches import create_search, get_search_results, list_searches

router = APIRouter()


@router.post("", response_model=CreateSearchResponse)
async def create_member_search(
    payload: ProductSearchRequest,
    request: Request,
    member: Annotated[CurrentMember, Depends(get_current_member)],
) -> CreateSearchResponse:
    return await create_search(member.id, payload, request.state.request_id)


@router.get("", response_model=list[SearchSummary])
async def list_member_searches(
    member: Annotated[CurrentMember, Depends(get_current_member)],
    limit: Annotated[int, Query(ge=1, le=5)] = 5,
) -> list[SearchSummary]:
    return await list_searches(member.id, limit)


@router.get("/{search_id}/results", response_model=SearchResultsResponse)
async def get_member_search_results(
    search_id: UUID, member: Annotated[CurrentMember, Depends(get_current_member)]
) -> SearchResultsResponse:
    return await get_search_results(member.id, search_id)
