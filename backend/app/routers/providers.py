"""API Router for Service Provider dashboard and management endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.booking import BookingOut, BookingStatusUpdate, ProviderDashboardSummary
from app.services.auth_service import get_current_provider
from app.services.booking_service import (
    get_provider_bookings,
    get_provider_dashboard_summary,
    update_booking_status,
)

router = APIRouter(prefix="/providers", tags=["Provider Management"])


@router.get(
    "/dashboard",
    response_model=ProviderDashboardSummary,
    summary="Get Provider Dashboard Analytics Summary",
    description="Retrieves aggregate metrics, slot availability, total revenue, and upcoming schedule for provider."
)
async def get_dashboard(
    current_user: User = Depends(get_current_provider),
    db: AsyncSession = Depends(get_db)
) -> ProviderDashboardSummary:
    """Get dashboard metrics endpoint.

    Args:
        current_user (User): Current provider user.
        db (AsyncSession): Database session.

    Returns:
        ProviderDashboardSummary: Aggregate analytics object.
    """
    return await get_provider_dashboard_summary(db, current_user.id)


@router.get(
    "/bookings",
    response_model=List[BookingOut],
    summary="List Provider's incoming bookings",
    description="Retrieves bookings for services owned by provider with optional status filter."
)
async def list_provider_incoming_bookings(
    status: Optional[str] = Query(None, description="Filter by booking status"),
    current_user: User = Depends(get_current_provider),
    db: AsyncSession = Depends(get_db)
) -> List[BookingOut]:
    """Get provider incoming bookings endpoint.

    Args:
        status (Optional[str]): Status filter string.
        current_user (User): Current provider user.
        db (AsyncSession): Database session.

    Returns:
        List[BookingOut]: List of provider bookings.
    """
    return await get_provider_bookings(db, current_user.id, status_filter=status)


@router.patch(
    "/bookings/{booking_id}/status",
    response_model=BookingOut,
    summary="Update Booking Status (Provider only)",
    description="Updates status of an incoming appointment (e.g. mark completed or cancelled)."
)
async def update_status_of_booking(
    booking_id: int,
    status_in: BookingStatusUpdate,
    current_user: User = Depends(get_current_provider),
    db: AsyncSession = Depends(get_db)
) -> BookingOut:
    """Update booking status endpoint.

    Args:
        booking_id (int): Booking ID.
        status_in (BookingStatusUpdate): New status value.
        current_user (User): Current provider user.
        db (AsyncSession): Database session.

    Returns:
        BookingOut: Updated booking object.
    """
    return await update_booking_status(
        db, booking_id, current_user.id, new_status=status_in.status
    )
