"""Service management business logic layer."""

from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.service import Service
from app.models.user import User
from app.schemas.service import ServiceCreate, ServiceUpdate


async def create_service(
    db: AsyncSession, provider_id: int, service_in: ServiceCreate
) -> Service:
    """Create a new service offered by a provider.

    Args:
        db (AsyncSession): Database session.
        provider_id (int): Provider user ID creating the service.
        service_in (ServiceCreate): Service creation payload.

    Returns:
        Service: Created Service ORM instance.
    """
    service = Service(
        provider_id=provider_id,
        name=service_in.name,
        description=service_in.description,
        duration_minutes=service_in.duration_minutes,
        price=service_in.price,
        is_active=service_in.is_active
    )
    db.add(service)
    await db.commit()
    await db.refresh(service)
    
    # Reload with provider relationship
    stmt = select(Service).options(selectinload(Service.provider)).where(Service.id == service.id)
    res = await db.execute(stmt)
    return res.scalar_one()


async def get_all_services(
    db: AsyncSession,
    provider_id: Optional[int] = None,
    search: Optional[str] = None
) -> List[Service]:
    """Retrieve all active public services, optionally filtered by provider or search term.

    Args:
        db (AsyncSession): Database session.
        provider_id (Optional[int]): Optional provider ID filter.
        search (Optional[str]): Optional title/description search query.

    Returns:
        List[Service]: List of active Service ORM instances.
    """
    stmt = select(Service).options(selectinload(Service.provider)).where(Service.is_active == True)

    if provider_id is not None:
        stmt = stmt.where(Service.provider_id == provider_id)

    if search:
        search_fmt = f"%{search}%"
        stmt = stmt.where(
            (Service.name.ilike(search_fmt)) | (Service.description.ilike(search_fmt))
        )

    stmt = stmt.order_by(Service.name.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_service_by_id(db: AsyncSession, service_id: int) -> Service:
    """Retrieve service details by service ID.

    Args:
        db (AsyncSession): Database session.
        service_id (int): Service ID.

    Returns:
        Service: Service ORM instance with provider loaded.

    Raises:
        HTTPException: 404 Not Found if service does not exist.
    """
    stmt = (
        select(Service)
        .options(selectinload(Service.provider))
        .where(Service.id == service_id)
    )
    result = await db.execute(stmt)
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID {service_id} not found."
        )
    return service


async def get_provider_services(db: AsyncSession, provider_id: int) -> List[Service]:
    """Retrieve all services (active and inactive) owned by a provider.

    Args:
        db (AsyncSession): Database session.
        provider_id (int): Provider user ID.

    Returns:
        List[Service]: List of provider's Service ORM instances.
    """
    stmt = (
        select(Service)
        .options(selectinload(Service.provider))
        .where(Service.provider_id == provider_id)
        .order_by(Service.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_service(
    db: AsyncSession,
    service_id: int,
    provider_id: int,
    service_in: ServiceUpdate
) -> Service:
    """Update an existing service owned by the specified provider.

    Args:
        db (AsyncSession): Database session.
        service_id (int): ID of service to update.
        provider_id (int): Provider user ID performing update.
        service_in (ServiceUpdate): Fields to update.

    Returns:
        Service: Updated Service ORM instance.

    Raises:
        HTTPException: 404 Not Found if service doesn't exist, or 403 Forbidden if owned by another provider.
    """
    service = await get_service_by_id(db, service_id)

    if service.provider_id != provider_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this service."
        )

    update_data = service_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)

    await db.commit()
    await db.refresh(service)
    return service


async def delete_service(
    db: AsyncSession, service_id: int, provider_id: int
) -> None:
    """Delete (or mark inactive) a service owned by provider.

    Args:
        db (AsyncSession): Database session.
        service_id (int): Service ID to delete.
        provider_id (int): Provider user ID.

    Raises:
        HTTPException: 404 Not Found or 403 Forbidden.
    """
    service = await get_service_by_id(db, service_id)

    if service.provider_id != provider_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this service."
        )

    await db.delete(service)
    await db.commit()
