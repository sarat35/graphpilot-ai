from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth.dependencies import CurrentMember, get_current_member
from app.config.settings import settings
from app.main import app
from app.services.searches import mock_search_repository


def member() -> CurrentMember:
    return CurrentMember(id=uuid4(), email="member@example.com")


def test_member_can_create_and_retrieve_own_mock_search(monkeypatch) -> None:
    monkeypatch.setattr(settings, "product_search_mode", "mock")
    current_member = member()
    app.dependency_overrides[get_current_member] = lambda: current_member
    mock_search_repository.clear()
    try:
        with TestClient(app) as client:
            create_response = client.post(
                "/api/v1/searches",
                json={"city": "Hyderabad", "brand": "Maruti Suzuki", "model": "Swift", "limit": 2},
            )
            search_id = create_response.json()["search"]["id"]
            list_response = client.get("/api/v1/searches")
            results_response = client.get(f"/api/v1/searches/{search_id}/results")
    finally:
        app.dependency_overrides.clear()
        mock_search_repository.clear()

    assert create_response.status_code == 200
    assert create_response.json()["search"]["status"] == "ready"
    assert create_response.json()["search"]["model"] == "Swift"
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == search_id
    assert results_response.status_code == 200
    assert len(results_response.json()["results"]) == 2


def test_member_cannot_read_another_members_search(monkeypatch) -> None:
    monkeypatch.setattr(settings, "product_search_mode", "mock")
    owner = member()
    other_member = member()
    mock_search_repository.clear()
    app.dependency_overrides[get_current_member] = lambda: owner
    try:
        with TestClient(app) as client:
            create_response = client.post("/api/v1/searches", json={"city": "Hyderabad"})
            search_id = create_response.json()["search"]["id"]
        app.dependency_overrides[get_current_member] = lambda: other_member
        with TestClient(app) as client:
            results_response = client.get(f"/api/v1/searches/{search_id}/results")
    finally:
        app.dependency_overrides.clear()
        mock_search_repository.clear()

    assert results_response.status_code == 404
