from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_cars() -> list[dict[str, str | int]]:
    """Return demonstration listings until marketplace search is connected."""
    return [
        {
            "id": "creta-2020-mumbai",
            "make": "Hyundai",
            "model": "Creta",
            "year": 2020,
            "price": 1350000,
            "city": "Mumbai",
            "kilometres": 41200,
            "match_percent": 94,
        },
        {
            "id": "seltos-2022-bengaluru",
            "make": "Kia",
            "model": "Seltos",
            "year": 2022,
            "price": 1580000,
            "city": "Bengaluru",
            "kilometres": 21300,
            "match_percent": 88,
        },
    ]
