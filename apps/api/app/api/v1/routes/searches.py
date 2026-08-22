from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_searches() -> list[dict[str, str | int]]:
    """Return demonstration saved searches until persistence is connected."""
    return [
        {
            "id": "search-bengaluru-maruti",
            "city": "Bengaluru",
            "brand": "Maruti Suzuki",
            "max_price": 700000,
        },
        {"id": "search-pune-petrol", "city": "Pune", "fuel_type": "petrol", "max_age": 4},
    ]
