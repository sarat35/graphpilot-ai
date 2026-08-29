from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import CurrentMember, get_current_member
from app.schemas.external_listings import SavedExternalListing, SaveExternalListingRequest
from app.services.external_listings import get_saved_external_listing, save_external_listing

router = APIRouter()


@router.post("", response_model=SavedExternalListing, status_code=status.HTTP_201_CREATED)
async def save_member_external_listing(
    payload: SaveExternalListingRequest,
    member: Annotated[CurrentMember, Depends(get_current_member)],
) -> SavedExternalListing:
    return await save_external_listing(member.id, payload)


@router.get("/{saved_listing_id}", response_model=SavedExternalListing)
async def open_member_external_listing(
    saved_listing_id: UUID,
    member: Annotated[CurrentMember, Depends(get_current_member)],
) -> SavedExternalListing:
    # Opening a saved listing is intentionally the only automatic refresh trigger.
    return await get_saved_external_listing(member.id, saved_listing_id, refresh=True)
