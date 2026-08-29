from uuid import UUID

from fastapi import HTTPException, status

from app.config.settings import settings
from app.repositories.postgres_searches import PostgresSearchRepository
from app.repositories.supabase_searches import SupabaseSearchRepository
from app.schemas.external_listings import SavedExternalListing, SaveExternalListingRequest


def _repository() -> PostgresSearchRepository | SupabaseSearchRepository:
    if settings.product_search_mode.lower() == "mock":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Saved external listings require the configured database.",
        )
    if settings.supabase_url and (
        settings.supabase_secret_key or settings.supabase_service_role_key
    ):
        return SupabaseSearchRepository(
            settings.supabase_url,
            settings.supabase_secret_key or settings.supabase_service_role_key,
        )
    if not settings.database_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Saved external listings require Supabase or a configured database.",
        )
    return PostgresSearchRepository(settings.database_url)


async def save_external_listing(
    user_id: UUID, payload: SaveExternalListingRequest
) -> SavedExternalListing:
    saved = await _repository().save_external_listing(user_id, payload.search_id, payload.rank)
    if saved is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search result not found")
    return saved


async def get_saved_external_listing(
    user_id: UUID, saved_listing_id: UUID, refresh: bool
) -> SavedExternalListing:
    saved = await _repository().get_saved_external_listing(user_id, saved_listing_id, refresh)
    if saved is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved listing not found")
    return saved
