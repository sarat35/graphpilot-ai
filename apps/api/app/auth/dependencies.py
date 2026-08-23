from functools import lru_cache
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError, PyJWKClient
from pydantic import BaseModel, ValidationError

from app.config.settings import settings

bearer_scheme = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]


class CurrentMember(BaseModel):
    id: UUID
    email: str | None = None


class TokenClaims(BaseModel):
    sub: UUID
    role: str
    email: str | None = None


@lru_cache
def get_jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url, cache_keys=True)


def get_jwks_url() -> str:
    if settings.supabase_jwks_url:
        return settings.supabase_jwks_url
    if settings.supabase_url:
        return f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    raise RuntimeError("Supabase JWT verification is not configured")


def decode_access_token(token: str) -> TokenClaims:
    """Verify signature, issuer, audience, expiration, and authenticated role."""
    try:
        signing_key = get_jwks_client(get_jwks_url()).get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256", "EdDSA"],
            audience=settings.supabase_jwt_audience,
            issuer=settings.supabase_jwt_issuer or f"{settings.supabase_url.rstrip('/')}/auth/v1",
            options={"require": ["sub", "exp", "iss", "aud"]},
        )
        claims = TokenClaims.model_validate(payload)
    except (InvalidTokenError, ValidationError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    return claims


def current_member_from_claims(claims: TokenClaims) -> CurrentMember:
    if claims.role != "authenticated":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentMember(id=claims.sub, email=claims.email)


def get_current_member(credentials: BearerCredentials) -> CurrentMember:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    claims = decode_access_token(credentials.credentials)
    return current_member_from_claims(claims)
