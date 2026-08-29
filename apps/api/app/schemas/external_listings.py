from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.product_search import ListingAvailability


class SaveExternalListingRequest(BaseModel):
    search_id: UUID
    rank: int = Field(ge=1, le=10)


class SavedExternalListing(BaseModel):
    id: UUID
    source_url: HttpUrl
    title: str
    source_name: str
    availability: ListingAvailability
    last_checked_at: datetime | None = None
    saved_at: datetime
