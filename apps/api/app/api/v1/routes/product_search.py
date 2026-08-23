from uuid import uuid4

from fastapi import APIRouter, Request

from app.schemas.product_search import ProductSearchRequest, ProductSearchResponse
from app.services.product_search import search_products

router = APIRouter()


@router.post("", response_model=ProductSearchResponse)
async def create_product_search(
    payload: ProductSearchRequest, request: Request
) -> ProductSearchResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    return await search_products(payload, request_id)
