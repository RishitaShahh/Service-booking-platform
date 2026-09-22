"""Booking core business logic layer enforcing slot concurrency, status transitions, and provider scoping."""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.booking import Booking, BookingStatus
from app.models.service import Service
from app.models.slot import SlotStatus, TimeSlot
from app.models.user import User
from app.schemas.booking import BookingCreate, ProviderDashboardSummary


async def create_booking(
    db: AsyncSession, customer_id: int, booking_in: BookingCreate
) -> Booking:
    """Create a new customer appointment booking with DB-level concurrency locking.

    Enforces Business Rules 1 & 2:
    - Atomically inspects and locks the requested time slot (`with_for_update`).
    - Verifies the slot is currently 'available'.
    - Updates slot status to 'booked' and creates Booking with status 'confirmed'.
    - If a race condition occurs or DB unique constraint fails, catches
      IntegrityError and returns HTTP 409 Conflict.

    Args:
        db (AsyncSession): Database session.
        customer_id (int): ID of the customer making the reservation.
        booking_in (BookingCreate): Booking payload containing service_id and slot_id.

    Returns:
        Booking: Created Booking ORM record with relationships populated.

    Raises:
        HTTPException: 404 Not Found if service/slot does not exist.
        HTTPException: 400 Bad Request if slot unavailable or invalid.
        HTTPException: 409 Conflict if time slot was booked by another concurrent request.
    """
    # 1. Fetch service record
    service_stmt = select(Service).where(Service.id == booking_in.service_id)
    service_res = await db.execute(service_stmt)
    service = service_res.scalar_one_or_none()

    if not service or not service.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The selected service is not active or does not exist."
        )

    # 2. Lock target time slot row for update (prevents race condition)
    slot_stmt = (
        select(TimeSlot)
        .where(TimeSlot.id == booking_in.slot_id)
        .with_for_update()
    )
    slot_res = await db.execute(slot_stmt)
    slot = slot_res.scalar_one_or_none()

    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested time slot was not found."
        )

    # 3. Check availability status (Business Rule 2)
    if slot.status != SlotStatus.AVAILABLE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This time slot is no longer available for booking."
        )

    # Verify slot belongs to the service provider
    if slot.provider_id != service.provider_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time slot provider does not match the service provider."
        )

    # If slot was unassigned, associate with this service
    if slot.service_id is None:
        slot.service_id = service.id

    # 4. Atomic state transition: Mark slot as booked & create booking
    slot.status = SlotStatus.BOOKED.value

    booking = Booking(
        customer_id=customer_id,
        service_id=service.id,
        provider_id=service.provider_id,
        slot_id=slot.id,
        status=BookingStatus.CONFIRMED.value,
        notes=booking_in.notes,
        booking_timestamp=datetime.now(timezone.utc)
    )

    try:
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A race condition occurred: this time slot was booked by another user."
        )

    # Query created booking with full relationship objects for response payload
    full_booking_stmt = (
        select(Booking)
        .options(
            selectinload(Booking.customer),
            selectinload(Booking.provider),
            selectinload(Booking.service),
            selectinload(Booking.slot),
        )
        .where(Booking.id == booking.id)
    )
    full_res = await db.execute(full_booking_stmt)
    return full_res.scalar_one()


async def cancel_booking(
    db: AsyncSession, booking_id: int, user_id: int, is_provider: bool = False
) -> Booking:
    """Cancel an existing booking reservation and automatically release slot back to 'available'.

    Enforces Business Rules 3 & 5:
    - Verifies ownership (Customer owns booking OR Provider owns service/slot).
    - Transitions booking status to 'cancelled'.
    - Automatically updates slot status back to 'available'.

    Args:
        db (AsyncSession): Database session.
        booking_id (int): ID of booking to cancel.
        user_id (int): Authenticated user ID attempting cancellation.
        is_provider (bool): True if user is a provider, False if customer.

    Returns:
        Booking: Updated Booking ORM record.

    Raises:
        HTTPException: 404 Not Found if booking missing.
        HTTPException: 403 Forbidden if user lacks ownership.
        HTTPException: 400 Bad Request if booking already cancelled or completed.
    """
    stmt = (
        select(Booking)
        .options(
            selectinload(Booking.slot),
            selectinload(Booking.customer),
            selectinload(Booking.provider),
            selectinload(Booking.service),
        )
        .where(Booking.id == booking_id)
    )
    res = await db.execute(stmt)
    booking = res.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found."
        )

    # Permission check (Business Rule 5: Provider/Customer scoping)
    if is_provider:
        if booking.provider_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to cancel this booking."
            )
    else:
        if booking.customer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to cancel this booking."
            )

    if booking.status == BookingStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled."
        )

    # Update booking status
    booking.status = BookingStatus.CANCELLED.value

    # Business Rule 3: Automatically release time slot back to 'available'
    if booking.slot:
        booking.slot.status = SlotStatus.AVAILABLE.value

    await db.commit()
    await db.refresh(booking)
    return booking


async def get_customer_bookings(
    db: AsyncSession, customer_id: int, status_filter: Optional[str] = None
) -> List[Booking]:
    """Retrieve booking history for a specific customer.

    Args:
        db (AsyncSession): Database session.
        customer_id (int): Customer user ID.
        status_filter (Optional[str]): Optional filter by BookingStatus string.

    Returns:
        List[Booking]: List of Booking records owned by customer.
    """
    stmt = (
        select(Booking)
        .options(
            selectinload(Booking.customer),
            selectinload(Booking.provider),
            selectinload(Booking.service),
            selectinload(Booking.slot),
        )
        .where(Booking.customer_id == customer_id)
    )

    if status_filter:
        stmt = stmt.where(Booking.status == status_filter)

    stmt = stmt.order_by(Booking.created_at.desc())
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def get_provider_bookings(
    db: AsyncSession, provider_id: int, status_filter: Optional[str] = None
) -> List[Booking]:
    """Retrieve bookings for a specific provider (Enforces Business Rule 5: strict provider scoping).

    Args:
        db (AsyncSession): Database session.
        provider_id (int): Provider user ID.
        status_filter (Optional[str]): Optional filter by status.

    Returns:
        List[Booking]: List of provider's incoming bookings.
    """
    stmt = (
        select(Booking)
        .options(
            selectinload(Booking.customer),
            selectinload(Booking.provider),
            selectinload(Booking.service),
            selectinload(Booking.slot),
        )
        .where(Booking.provider_id == provider_id)
    )

    if status_filter:
        stmt = stmt.where(Booking.status == status_filter)

    stmt = stmt.order_by(Booking.created_at.desc())
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def update_booking_status(
    db: AsyncSession, booking_id: int, provider_id: int, new_status: BookingStatus
) -> Booking:
    """Update status of a booking by provider (e.g., mark completed or cancelled).

    Args:
        db (AsyncSession): Database session.
        booking_id (int): Booking ID.
        provider_id (int): Provider user ID.
        new_status (BookingStatus): Target status enum.

    Returns:
        Booking: Updated Booking record.

    Raises:
        HTTPException: 404 Not Found, 403 Forbidden.
    """
    if new_status == BookingStatus.CANCELLED:
        return await cancel_booking(db, booking_id, provider_id, is_provider=True)

    stmt = (
        select(Booking)
        .options(
            selectinload(Booking.slot),
            selectinload(Booking.customer),
            selectinload(Booking.provider),
            selectinload(Booking.service),
        )
        .where(Booking.id == booking_id)
    )
    res = await db.execute(stmt)
    booking = res.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found."
        )

    if booking.provider_id != provider_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage this booking."
        )

    booking.status = new_status.value
    await db.commit()
    await db.refresh(booking)
    return booking


async def get_provider_dashboard_summary(
    db: AsyncSession, provider_id: int
) -> ProviderDashboardSummary:
    """Compute and aggregate summary analytics for provider dashboard.

    Args:
        db (AsyncSession): Database session.
        provider_id (int): Provider user ID.

    Returns:
        ProviderDashboardSummary: Aggregate dashboard statistics.
    """
    services_count_stmt = select(func.count(Service.id)).where(Service.provider_id == provider_id)
    services_count = (await db.execute(services_count_stmt)).scalar() or 0

    slots_count_stmt = select(func.count(TimeSlot.id)).where(TimeSlot.provider_id == provider_id)
    total_slots = (await db.execute(slots_count_stmt)).scalar() or 0

    available_slots_stmt = select(func.count(TimeSlot.id)).where(
        TimeSlot.provider_id == provider_id, TimeSlot.status == SlotStatus.AVAILABLE.value
    )
    available_slots = (await db.execute(available_slots_stmt)).scalar() or 0

    total_bookings_stmt = select(func.count(Booking.id)).where(Booking.provider_id == provider_id)
    total_bookings = (await db.execute(total_bookings_stmt)).scalar() or 0

    upcoming_count_stmt = select(func.count(Booking.id)).where(
        Booking.provider_id == provider_id,
        Booking.status.in_([BookingStatus.CONFIRMED.value, BookingStatus.PENDING.value])
    )
    upcoming_count = (await db.execute(upcoming_count_stmt)).scalar() or 0

    completed_count_stmt = select(func.count(Booking.id)).where(
        Booking.provider_id == provider_id,
        Booking.status == BookingStatus.COMPLETED.value
    )
    completed_count = (await db.execute(completed_count_stmt)).scalar() or 0

    revenue_stmt = (
        select(func.coalesce(func.sum(Service.price), 0.0))
        .select_from(Booking)
        .join(Service, Booking.service_id == Service.id)
        .where(
            Booking.provider_id == provider_id,
            Booking.status.in_([BookingStatus.CONFIRMED.value, BookingStatus.COMPLETED.value])
        )
    )
    revenue = (await db.execute(revenue_stmt)).scalar() or 0.0

    upcoming_bookings_list = await get_provider_bookings(
        db, provider_id, status_filter=BookingStatus.CONFIRMED.value
    )

    return ProviderDashboardSummary(
        total_services=services_count,
        total_slots=total_slots,
        available_slots=available_slots,
        total_bookings=total_bookings,
        upcoming_bookings_count=upcoming_count,
        completed_bookings_count=completed_count,
        total_revenue=float(revenue),
        upcoming_bookings=upcoming_bookings_list
    )
