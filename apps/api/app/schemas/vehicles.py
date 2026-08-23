from pydantic import BaseModel, Field, HttpUrl


class Vehicle(BaseModel):
    id: str = Field(min_length=1, max_length=120)
    make: str
    model: str
    variant: str
    year: int = Field(ge=1950, le=2100)
    fuel_type: str
    transmission: str
    price_inr: int = Field(ge=0)
    kilometres: int = Field(ge=0)
    city: str
    source_name: str
    source_url: HttpUrl
    seller_type: str
    description: str
    condition_notes: str


class SavedVehicle(BaseModel):
    id: str
    vehicle: Vehicle
    saved_at: str


class SaveVehicleRequest(BaseModel):
    vehicle_id: str = Field(min_length=1, max_length=120)
