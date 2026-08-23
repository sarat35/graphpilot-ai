from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl, field_validator


class FuelType(StrEnum):
    PETROL = "petrol"
    DIESEL = "diesel"
    CNG = "cng"
    ELECTRIC = "electric"
    HYBRID = "hybrid"


class ProductSearchRequest(BaseModel):
    city: str = Field(min_length=2, max_length=80)
    min_price_inr: int | None = Field(default=None, ge=0, le=50_000_000)
    max_price_inr: int | None = Field(default=None, ge=1, le=50_000_000)
    brand: str | None = Field(default=None, min_length=2, max_length=80)
    model: str | None = Field(default=None, min_length=1, max_length=100)
    fuel_type: FuelType | None = None
    max_age_years: int | None = Field(default=None, ge=0, le=30)
    max_kilometres: int | None = Field(default=None, ge=0, le=1_000_000)
    limit: int = Field(default=5, ge=1, le=5)

    @field_validator("city", "brand", "model", mode="before")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    def model_post_init(self, __context: object) -> None:
        if self.min_price_inr and self.max_price_inr and self.min_price_inr > self.max_price_inr:
            raise ValueError("min_price_inr must not exceed max_price_inr")


class ProductListing(BaseModel):
    vehicle_id: str | None = Field(default=None, max_length=120)
    title: str = Field(min_length=1, max_length=300)
    source_url: HttpUrl
    source_name: str = Field(min_length=1, max_length=100)
    snippet: str = Field(default="", max_length=2_000)
    price_inr: int | None = Field(default=None, ge=0)
    year: int | None = Field(default=None, ge=1900, le=2100)
    kilometres: int | None = Field(default=None, ge=0)


class ProductSearchResponse(BaseModel):
    query: str
    results: list[ProductListing] = Field(max_length=5)
    result_source: str
    model_name: str
    request_id: str
