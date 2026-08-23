from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth.dependencies import CurrentMember, get_current_member
from app.main import app
from app.services.vehicles import mock_vehicle_repository


def test_member_can_save_and_remove_a_vehicle() -> None:
    member = CurrentMember(id=uuid4(), email="member@example.com")
    app.dependency_overrides[get_current_member] = lambda: member
    mock_vehicle_repository.clear()
    try:
        with TestClient(app) as client:
            saved = client.post("/api/v1/saved-vehicles", json={"vehicle_id": "swift-vxi-amt"})
            listed = client.get("/api/v1/saved-vehicles")
            removed = client.delete("/api/v1/saved-vehicles/swift-vxi-amt")
    finally:
        app.dependency_overrides.clear()
        mock_vehicle_repository.clear()

    assert saved.status_code == 201
    assert listed.json()[0]["vehicle"]["id"] == "swift-vxi-amt"
    assert removed.status_code == 204


def test_member_cannot_save_unknown_vehicle() -> None:
    member = CurrentMember(id=uuid4(), email="member@example.com")
    app.dependency_overrides[get_current_member] = lambda: member
    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/saved-vehicles", json={"vehicle_id": "missing"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
