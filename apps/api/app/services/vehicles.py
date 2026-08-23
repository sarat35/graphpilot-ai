from uuid import UUID

from fastapi import HTTPException, status

from app.repositories.mock_vehicles import MockVehicleRepository
from app.schemas.vehicles import SavedVehicle, Vehicle

mock_vehicle_repository = MockVehicleRepository()


async def get_vehicle(vehicle_id: str) -> Vehicle:
    vehicle = await mock_vehicle_repository.get(vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return vehicle


async def list_saved_vehicles(user_id: UUID) -> list[SavedVehicle]:
    return await mock_vehicle_repository.list_saved(user_id)


async def save_vehicle(user_id: UUID, vehicle_id: str) -> SavedVehicle:
    vehicle = await get_vehicle(vehicle_id)
    try:
        return await mock_vehicle_repository.save(user_id, vehicle)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


async def remove_saved_vehicle(user_id: UUID, vehicle_id: str) -> None:
    removed = await mock_vehicle_repository.remove(user_id, vehicle_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved vehicle not found")
