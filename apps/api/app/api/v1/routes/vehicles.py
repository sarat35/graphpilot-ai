from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.auth.dependencies import CurrentMember, get_current_member
from app.schemas.vehicles import SavedVehicle, SaveVehicleRequest, Vehicle
from app.services.vehicles import (
    get_vehicle,
    list_saved_vehicles,
    remove_saved_vehicle,
    save_vehicle,
)

router = APIRouter()


@router.get("/{vehicle_id}", response_model=Vehicle)
async def get_member_vehicle(vehicle_id: str) -> Vehicle:
    return await get_vehicle(vehicle_id)


@router.get("/", response_model=list[Vehicle])
async def list_vehicles() -> list[Vehicle]:
    from app.repositories.mock_vehicles import MOCK_VEHICLES

    return MOCK_VEHICLES


saved_router = APIRouter()


@saved_router.get("", response_model=list[SavedVehicle])
async def list_member_saved_vehicles(
    member: Annotated[CurrentMember, Depends(get_current_member)],
) -> list[SavedVehicle]:
    return await list_saved_vehicles(member.id)


@saved_router.post("", response_model=SavedVehicle, status_code=status.HTTP_201_CREATED)
async def save_member_vehicle(
    payload: SaveVehicleRequest, member: Annotated[CurrentMember, Depends(get_current_member)]
) -> SavedVehicle:
    return await save_vehicle(member.id, payload.vehicle_id)


@saved_router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member_saved_vehicle(
    vehicle_id: str,
    member: Annotated[CurrentMember, Depends(get_current_member)],
) -> Response:
    await remove_saved_vehicle(member.id, vehicle_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
