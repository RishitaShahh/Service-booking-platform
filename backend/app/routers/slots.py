"""API Router for time slot availability management endpoints."""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.slot import SlotBatchCreate, SlotCreate, SlotOut
from app.services.auth_service import get_current_provider
from app.services.slot_service import (
    batch_create_slots,
    create_slot,
    delete_slot,
    get_available_slots,
    get_provider_slots,
)

router = APIRouter(prefix="/slots", tags=["Time Slots"])


@router.get(
    "",
    response_model=List[SlotOut],
    summary="List available time slots",
    description="Retrieves available time slots for booking, with optional service, provider, and start_date filters."
)
async def list_available_slots(
    service_id: Optional[int] = Query(None, description="Filter slots by service ID"),
    provider_id: Optional[int] = Query(None, description="Filter slots by provider ID"),
    start_date: Optional[datetime] = Query(None, description="Filter slots on or after this timestamp"),
    db: AsyncSession = Depends(get_db)
) -> List[SlotOut]:
    """Get available slots endpoint.

    Args:
        service_id (Optional[int]): Optional service filter.
        provider_id (Optional[int]): Optional provider filter.
        start_date (Optional[datetime]): Optional date filter.
        db (AsyncSession): Database session.

    Returns:
        List[SlotOut]: Matching available time slots.
    """
    return await get_available_slots(
        db, service_id=service_id, provider_id=provider_id, start_date=start_date
    )


@router.get(
    "/provider/my-slots",
    response_model=List[SlotOut],
    summary="List provider's created slots",
    description="Retrieves all time slots created by the authenticated provider."
)
async def list_my_slots(
    current_user: User = Depends(get_current_provider),
    db: AsyncSession = Depends(get_db)
) -> List[SlotOut]:
    """Get provider slots endpoint.

    Args:
        current_user (User): Current provider user.
        db (AsyncSession): Database session.

    Returns:
        List[SlotOut]: Provider slots.
    """
    return await get_provider_slots(db, current_user.id)


@router.post(
    "",
    response_model=SlotOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a single time slot (Provider only)",
    description="Creates a new time slot window offered by provider."
)
async def create_single_slot(
    slot_in: SlotCreate,
    current_user: User = Depends(get_current_provider),
    db: AsyncSession = Depends(get_db)
) -> SlotOut:
    """Create single slot endpoint.

    Args:
        slot_in (SlotCreate): Slot creation payload.
        current_user (User): Current provider user.
        db (AsyncSession): Database session.

    Returns:
        SlotOut: Created slot object.
    """
    return await create_slot(db, current_user.id, slot_in)


@router.post(
    "/batch",
    response_model=List[SlotOut],
    status_code=status.HTTP_201_CREATED,
    summary="Batch generate time slots for a day (Provider only)",
    description="Generates recurring time slot windows for a specific date and hour range."
)
async def batch_generate_slots(
    batch_in: SlotBatchCreate,
    current_user: User = Depends(get_current_provider),
    db: AsyncSession = Depends(get_db)
) -> List[SlotOut]:
    """Batch slot generation endpoint.

    Args:
        batch_in (SlotBatchCreate): Batch configuration parameters.
        current_user (User): Current provider user.
        db (AsyncSession): Database session.

    Returns:
        List[SlotOut]: List of created slot objects.
    """
    return await batch_create_slots(db, current_user.id, batch_in)


@router.delete(
    "/{slot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an unbooked time slot (Provider only)",
    description="Deletes an unbooked time slot created by the authenticated provider."
)
async def delete_existing_slot(
    slot_id: int,
    current_user: User = Depends(get_current_provider),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete slot endpoint.

    Args:
        slot_id (int): Target slot ID.
        current_user (User): Current provider user.
        db (AsyncSession): Database session.
    """
    await delete_slot(db, slot_id, current_user.id)
