from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_saved_cars() -> list[dict[str, str | int]]:
    """Return demonstration saved cars until persistence is connected."""
    return [{"car_id": "creta-2020-mumbai", "saved_at": "2026-08-22T00:00:00Z", "rank": 1}]
