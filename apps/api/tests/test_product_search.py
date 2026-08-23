from fastapi.testclient import TestClient

from app.auth.dependencies import CurrentMember, get_current_member
from app.config.settings import settings
from app.main import app


def authenticated_member() -> CurrentMember:
    return CurrentMember(id="11111111-1111-1111-1111-111111111111", email="member@example.com")


def test_product_search_returns_structured_mock_results(monkeypatch) -> None:
    monkeypatch.setattr(settings, "product_search_mode", "mock")
    app.dependency_overrides[get_current_member] = authenticated_member
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/product-search",
                headers={"X-Request-ID": "product-search-test"},
                json={
                    "city": "Bengaluru",
                    "brand": "Maruti Suzuki",
                    "model": "Swift",
                    "fuel_type": "petrol",
                    "max_price_inr": 700000,
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["result_source"] == "mock_google_serper"
    assert body["request_id"] == "product-search-test"
    assert body["results"][0]["title"].startswith("2021 Maruti Suzuki Swift")
    assert body["results"][0]["source_url"].startswith("https://example.com/")


def test_product_search_validates_price_range() -> None:
    app.dependency_overrides[get_current_member] = authenticated_member
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/product-search",
                json={"city": "Pune", "min_price_inr": 900000, "max_price_inr": 500000},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
