from uuid import UUID, uuid4

from app.schemas.vehicles import SavedVehicle, Vehicle

MOCK_VEHICLES = [
    Vehicle(
        id="swift-vxi-amt",
        make="Maruti Suzuki",
        model="Swift",
        variant="VXI AMT",
        year=2021,
        fuel_type="Petrol",
        transmission="Automatic",
        price_inr=620000,
        kilometres=28500,
        city="Bengaluru",
        source_name="BuySeconds mock marketplace",
        source_url="https://example.com/listings/swift-vxi-amt",
        seller_type="Certified Dealer",
        description="Well-maintained single-owner hatchback with service records.",
        condition_notes="Minor door-edge scuff disclosed by seller.",
    ),
    Vehicle(
        id="seltos-gtx-turbo",
        make="Kia",
        model="Seltos",
        variant="GTX+ Turbo",
        year=2022,
        fuel_type="Petrol",
        transmission="Automatic",
        price_inr=1580000,
        kilometres=21300,
        city="Bengaluru",
        source_name="BuySeconds mock marketplace",
        source_url="https://example.com/listings/seltos-gtx-turbo",
        seller_type="Certified Dealer",
        description="Dealer-certified turbo SUV with low kilometres.",
        condition_notes="150-point inspection passed.",
    ),
]


class MockVehicleRepository:
    def __init__(self) -> None:
        self._saved: dict[UUID, dict[str, SavedVehicle]] = {}

    async def get(self, vehicle_id: str) -> Vehicle | None:
        return next((vehicle for vehicle in MOCK_VEHICLES if vehicle.id == vehicle_id), None)

    async def list_saved(self, user_id: UUID) -> list[SavedVehicle]:
        return list(self._saved.get(user_id, {}).values())

    async def save(self, user_id: UUID, vehicle: Vehicle) -> SavedVehicle:
        saved = self._saved.setdefault(user_id, {})
        if vehicle.id in saved:
            return saved[vehicle.id]
        if len(saved) >= 5:
            raise ValueError("SAVED_VEHICLE_LIMIT_REACHED")
        record = SavedVehicle(id=str(uuid4()), vehicle=vehicle, saved_at="2026-08-23T00:00:00Z")
        saved[vehicle.id] = record
        return record

    async def remove(self, user_id: UUID, vehicle_id: str) -> bool:
        return self._saved.get(user_id, {}).pop(vehicle_id, None) is not None

    def clear(self) -> None:
        self._saved.clear()
