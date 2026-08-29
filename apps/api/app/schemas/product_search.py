from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.config.settings import settings


class FuelType(StrEnum):
    PETROL = "petrol"
    DIESEL = "diesel"
    CNG = "cng"
    ELECTRIC = "electric"
    HYBRID = "hybrid"


class ListingAvailability(StrEnum):
    AVAILABLE = "available"
    EXPIRED = "expired"
    REMOVED = "removed"


class ProductSearchRequest(BaseModel):
    city: str = Field(min_length=2, max_length=80)
    min_price_inr: int | None = Field(default=None, ge=0, le=50_000_000)
    max_price_inr: int | None = Field(default=None, ge=1, le=50_000_000)
    brand: str | None = Field(default=None, min_length=2, max_length=80)
    model: str | None = Field(default=None, min_length=1, max_length=100)
    fuel_type: FuelType | None = None
    max_age_years: int | None = Field(default=None, ge=0, le=30)
    max_kilometres: int | None = Field(default=None, ge=0, le=1_000_000)
    limit: int = Field(default=10, ge=1, le=10)

    @field_validator("city", "brand", "model", mode="before")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    def model_post_init(self, __context: object) -> None:
        if self.city.casefold() != settings.product_search_allowed_city.casefold():
            raise ValueError(
                f"Only {settings.product_search_allowed_city} searches are currently supported"
            )
        if self.min_price_inr is not None and self.max_price_inr is not None:
            if self.min_price_inr > self.max_price_inr:
                raise ValueError("min_price_inr must not exceed max_price_inr")


class ProductListing(BaseModel):
    vehicle_id: str | None = Field(default=None, max_length=255)
    title: str = Field(min_length=1, max_length=300)
    source_url: HttpUrl
    source_name: str = Field(min_length=1, max_length=120)
    snippet: str = Field(default="", max_length=2_000)
    city: str | None = Field(default=None, max_length=80)
    make: str | None = Field(default=None, max_length=120)
    model: str | None = Field(default=None, max_length=120)
    variant: str | None = Field(default=None, max_length=160)
    price_inr: int | None = Field(default=None, ge=0)
    year: int | None = Field(default=None, ge=1900, le=2100)
    kilometres: int | None = Field(default=None, ge=0)
    fuel_type: FuelType | None = None
    transmission: str | None = Field(default=None, max_length=30)
    seller_type: str | None = Field(default=None, max_length=80)
    image_url: HttpUrl | None = None
    availability: ListingAvailability = ListingAvailability.AVAILABLE
    raw_source_data: dict[str, Any] = Field(default_factory=dict)
    retrieved_at: datetime | None = None


class RankedProductListing(ProductListing):
    rank: int = Field(ge=1, le=10)
    match_percentage: int = Field(ge=0, le=100)
    match_reasons: list[str] = Field(default_factory=list)
    unmatched_or_missing_reasons: list[str] = Field(default_factory=list)


class ProductSearchResponse(BaseModel):
    query: str
    results: list[RankedProductListing] = Field(max_length=10)
    result_source: str
    model_name: str
    request_id: str
