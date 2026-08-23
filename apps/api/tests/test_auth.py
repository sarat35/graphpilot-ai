from types import SimpleNamespace
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.auth.dependencies import (
    CurrentMember,
    TokenClaims,
    current_member_from_claims,
    decode_access_token,
    get_current_member,
)
from app.config.settings import settings
from app.main import app


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_protected_api_requires_a_bearer_token():
    with TestClient(app) as client:
        response = client.get("/api/v1/cars")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_protected_api_accepts_a_verified_member():
    member = CurrentMember(id=uuid4(), email="member@example.com")
    app.dependency_overrides[get_current_member] = lambda: member

    with TestClient(app) as client:
        response = client.get("/api/v1/cars")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_current_member_rejects_an_absent_credential():
    with pytest.raises(HTTPException) as error:
        get_current_member(None)

    assert error.value.status_code == 401


def test_token_claims_require_an_authenticated_role():
    claims = TokenClaims(sub=uuid4(), role="anon", email="member@example.com")

    with pytest.raises(HTTPException) as error:
        current_member_from_claims(claims)

    assert error.value.status_code == 401


def test_decode_access_token_verifies_supabase_claims(monkeypatch):
    private_key = generate_private_key(public_exponent=65537, key_size=2048)
    user_id = uuid4()
    monkeypatch.setattr(settings, "supabase_jwt_issuer", "https://example.supabase.co/auth/v1")
    monkeypatch.setattr(settings, "supabase_jwt_audience", "authenticated")
    monkeypatch.setattr(
        "app.auth.dependencies.get_jwks_client",
        lambda _url: SimpleNamespace(
            get_signing_key_from_jwt=lambda _token: SimpleNamespace(key=private_key.public_key())
        ),
    )
    token = jwt.encode(
        {
            "sub": str(user_id),
            "role": "authenticated",
            "email": "member@example.com",
            "iss": "https://example.supabase.co/auth/v1",
            "aud": "authenticated",
            "exp": 4_000_000_000,
        },
        private_key,
        algorithm="RS256",
    )

    claims = decode_access_token(token)

    assert claims.sub == user_id
    assert claims.email == "member@example.com"


def test_decode_access_token_rejects_the_wrong_audience(monkeypatch):
    private_key = generate_private_key(public_exponent=65537, key_size=2048)
    monkeypatch.setattr(settings, "supabase_jwt_issuer", "https://example.supabase.co/auth/v1")
    monkeypatch.setattr(settings, "supabase_jwt_audience", "authenticated")
    monkeypatch.setattr(
        "app.auth.dependencies.get_jwks_client",
        lambda _url: SimpleNamespace(
            get_signing_key_from_jwt=lambda _token: SimpleNamespace(key=private_key.public_key())
        ),
    )
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "role": "authenticated",
            "iss": "https://example.supabase.co/auth/v1",
            "aud": "another-audience",
            "exp": 4_000_000_000,
        },
        private_key,
        algorithm="RS256",
    )

    with pytest.raises(HTTPException) as error:
        decode_access_token(token)

    assert error.value.status_code == 401
