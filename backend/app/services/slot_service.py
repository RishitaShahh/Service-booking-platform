"""TimeSlot management business logic layer."""

from datetime import datetime, time, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.service import Service
from app.models.slot import SlotStatus, TimeSlot
from app.schemas.slot import SlotBatchCreate, SlotCreate


async def create_slot(
    db: AsyncSession, provider_id: int, slot_in: SlotCreate
) -> TimeSlot:
    """Create a single time slot for provider.

    Args:
        db (AsyncSession): Database session.
        provider_id (int): Provider user ID.
        slot_in (SlotCreate): Slot details.

    Returns:
        TimeSlot: Created TimeSlot ORM instance.

    Raises:
        HTTPException: 400 Bad Request if end_time <= start_time.
    """
    if slot_in.end_time <= slot_in.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot end time must be after start time."
        )

    # Convert naive or UTC datetimes cleanly
    start_dt = slot_in.start_time.replace(tzinfo=None) if slot_in.start_time.tzinfo else slot_in.start_time
    end_dt = slot_in.end_time.replace(tzinfo=None) if slot_in.end_time.tzinfo else slot_in.end_time

    slot = TimeSlot(
        provider_id=provider_id,
        service_id=slot_in.service_id,
        start_time=start_dt,
        end_time=end_dt,
        status=slot_in.status.value
    )
    db.add(slot)
    await db.commit()
    await db.refresh(slot)

    stmt = (
        select(TimeSlot)
        .options(selectinload(TimeSlot.provider), selectinload(TimeSlot.service))
        .where(TimeSlot.id == slot.id)
    )
    res = await db.execute(stmt)
    return res.scalar_one()


async def batch_create_slots(
    db: AsyncSession, provider_id: int, batch_in: SlotBatchCreate
) -> List[TimeSlot]:
    """Batch generate recurring time slots across a target date window.

    Args:
        db (AsyncSession): Database session.
        provider_id (int): Provider user ID.
        batch_in (SlotBatchCreate): Batch definition details.

    Returns:
        List[TimeSlot]: Created TimeSlot ORM instances.
    """
    created_slots: List[TimeSlot] = []

    # Calculate start and end datetimes as naive datetimes representing target local hours
    start_dt = datetime.combine(
        batch_in.target_date, time(hour=batch_in.start_hour, minute=0)
    )
    
    end_dt = datetime.combine(
        batch_in.target_date, 
        time(hour=batch_in.end_hour - 1, minute=59, second=59) if batch_in.end_hour == 24 
        else time(hour=batch_in.end_hour, minute=0)
    )

    if end_dt <= start_dt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch end hour must be greater than start hour."
        )

    current_start = start_dt
    delta = timedelta(minutes=batch_in.slot_duration_minutes)

    while current_start + delta <= end_dt:
        current_end = current_start + delta
        slot = TimeSlot(
            provider_id=provider_id,
            service_id=batch_in.service_id,
            start_time=current_start,
            end_time=current_end,
            status=SlotStatus.AVAILABLE.value
        )
        db.add(slot)
        created_slots.append(slot)
        current_start = current_end

    await db.commit()

    slot_ids = [s.id for s in created_slots if s.id is not None]
    if not slot_ids:
        return []

    stmt = (
        select(TimeSlot)
        .options(selectinload(TimeSlot.provider), selectinload(TimeSlot.service))
        .where(TimeSlot.id.in_(slot_ids))
        .order_by(TimeSlot.start_time.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_available_slots(
    db: AsyncSession,
    service_id: Optional[int] = None,
    provider_id: Optional[int] = None,
    start_date: Optional[datetime] = None
) -> List[TimeSlot]:
    """Retrieve available time slots for booking (status == 'available').

    Args:
        db (AsyncSession): Database session.
        service_id (Optional[int]): Optional filter by service.
        provider_id (Optional[int]): Optional filter by provider.
        start_date (Optional[datetime]): Optional filter by date.

    Returns:
        List[TimeSlot]: Available slots matching criteria.
    """
    stmt = (
        select(TimeSlot)
        .options(selectinload(TimeSlot.provider), selectinload(TimeSlot.service))
        .where(TimeSlot.status == SlotStatus.AVAILABLE.value)
    )

    if service_id is not None:
        # Query service to get provider_id for unassigned slots matching this provider
        service_stmt = select(Service).where(Service.id == service_id)
        service_res = await db.execute(service_stmt)
        service_obj = service_res.scalar_one_or_none()
        
        if service_obj:
            stmt = stmt.where(
                (TimeSlot.service_id == service_id) |
                ((TimeSlot.provider_id == service_obj.provider_id) & (TimeSlot.service_id.is_(None)))
            )
        else:
            stmt = stmt.where(TimeSlot.service_id == service_id)

    if provider_id is not None:
        stmt = stmt.where(TimeSlot.provider_id == provider_id)

    if start_date:
        clean_start = start_date.replace(tzinfo=None) if start_date.tzinfo else start_date
        stmt = stmt.where(TimeSlot.start_time >= clean_start)

    stmt = stmt.order_by(TimeSlot.start_time.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_provider_slots(db: AsyncSession, provider_id: int) -> List[TimeSlot]:
    """Retrieve all slots created by provider.

    Args:
        db (AsyncSession): Database session.
        provider_id (int): Provider user ID.

    Returns:
        List[TimeSlot]: Provider's TimeSlot records.
    """
    stmt = (
        select(TimeSlot)
        .options(selectinload(TimeSlot.provider), selectinload(TimeSlot.service))
        .where(TimeSlot.provider_id == provider_id)
        .order_by(TimeSlot.start_time.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def delete_slot(db: AsyncSession, slot_id: int, provider_id: int) -> None:
    """Delete an unbooked time slot owned by provider.

    Args:
        db (AsyncSession): Database session.
        slot_id (int): Slot ID.
        provider_id (int): Provider user ID.

    Raises:
        HTTPException: 404 Not Found, 403 Forbidden, or 400 Bad Request if slot is booked.
    """
    stmt = select(TimeSlot).where(TimeSlot.id == slot_id)
    result = await db.execute(stmt)
    slot = result.scalar_one_or_none()

    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Slot with ID {slot_id} not found."
        )

    if slot.provider_id != provider_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this slot."
        )

    if slot.status == SlotStatus.BOOKED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a time slot that is currently booked. Cancel the booking first."
        )

    await db.delete(slot)
    await db.commit()
