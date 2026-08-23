from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.product_search import ProductListing


class SearchSummary(BaseModel):
    id: UUID
    city: str
    brand: str | None
    model: str | None
    fuel_type: str | None
    status: str
    result_count: int = Field(ge=0, le=5)
    created_at: datetime


class CreateSearchResponse(BaseModel):
    search: SearchSummary


class SearchResultsResponse(BaseModel):
    search: SearchSummary
    results: list[ProductListing] = Field(max_length=5)
