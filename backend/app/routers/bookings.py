"""API Router for customer booking reservation endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingOut
from app.services.auth_service import get_current_customer, get_current_user
from app.services.booking_service import (
    cancel_booking,
    create_booking,
    get_customer_bookings,
)

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=BookingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Book a service appointment (Customer only)",
    description="Reserves an available time slot for a service with concurrency race-condition locking."
)
async def create_new_booking(
    booking_in: BookingCreate,
    current_user: User = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
) -> BookingOut:
    """Create booking endpoint.

    Args:
        booking_in (BookingCreate): Booking creation payload.
        current_user (User): Authenticated customer.
        db (AsyncSession): Database session.

    Returns:
        BookingOut: Created booking record.
    """
    return await create_booking(db, current_user.id, booking_in)


@router.get(
    "/my-bookings",
    response_model=List[BookingOut],
    summary="List customer booking history (Customer only)",
    description="Retrieves list of bookings made by the authenticated customer."
)
async def list_my_bookings(
    status: Optional[str] = Query(None, description="Optional status filter ('confirmed', 'cancelled', 'completed')"),
    current_user: User = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
) -> List[BookingOut]:
    """Get customer booking history.

    Args:
        status (Optional[str]): Optional status filter.
        current_user (User): Authenticated customer.
        db (AsyncSession): Database session.

    Returns:
        List[BookingOut]: Customer bookings.
    """
    return await get_customer_bookings(db, current_user.id, status_filter=status)


@router.post(
    "/{booking_id}/cancel",
    response_model=BookingOut,
    summary="Cancel an appointment booking",
    description="Cancels a booking and automatically releases the time slot back to 'available' status."
)
async def cancel_existing_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> BookingOut:
    """Cancel booking endpoint.

    Args:
        booking_id (int): Target booking ID.
        current_user (User): Authenticated user (Customer or Provider).
        db (AsyncSession): Database session.

    Returns:
        BookingOut: Updated booking record with cancelled status.
    """
    is_provider = current_user.role == "provider"
    return await cancel_booking(db, booking_id, current_user.id, is_provider=is_provider)
