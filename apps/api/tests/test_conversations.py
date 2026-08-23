from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth.dependencies import CurrentMember, get_current_member
from app.main import app
from app.services.conversations import mock_conversation_repository


def test_conversation_extracts_city_and_returns_one_follow_up() -> None:
    member = CurrentMember(id=uuid4(), email="member@example.com")
    app.dependency_overrides[get_current_member] = lambda: member
    mock_conversation_repository.clear()
    try:
        with TestClient(app) as client:
            created = client.post("/api/v1/conversations")
            conversation_id = created.json()["conversation"]["id"]
            replied = client.post(
                f"/api/v1/conversations/{conversation_id}/messages",
                json={"content": "Show me hybrid vehicles in Hyderabad"},
            )
    finally:
        app.dependency_overrides.clear()
        mock_conversation_repository.clear()

    assert replied.status_code == 200
    body = replied.json()
    assert body["conversation"]["criteria"] == {"city": "hyderabad", "fuel_type": "hybrid"}
    assert body["messages"][-1]["content"].startswith("I found")
    assert "live matches" in body["messages"][-1]["content"]
