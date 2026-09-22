"""API Router for service catalog endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.service import ServiceCreate, ServiceOut, ServiceUpdate
from app.services.auth_service import get_current_provider
from app.services.service_service import (
    create_service,
    delete_service,
    get_all_services,
    get_provider_services,
    get_service_by_id,
    update_service,
)

router = APIRouter(prefix="/services", tags=["Services"])


@router.get(
    "",
    response_model=List[ServiceOut],
    summary="List active services catalog",
    description="Retrieves a list of active services available for customer booking."
)
async def list_services(
    provider_id: Optional[int] = Query(None, description="Filter by provider user ID"),
    search: Optional[str] = Query(None, description="Search query string"),
    db: AsyncSession = Depends(get_db)
) -> List[ServiceOut]:
    """List active services.

    Args:
        provider_id (Optional[int]): Optional provider ID filter.
        search (Optional[str]): Optional search query.
        db (AsyncSession): Database session.

    Returns:
        List[ServiceOut]: List of active service models.
    """
    return await get_all_services(db, provider_id=provider_id, search=search)


@router.get(
    "/provider/my-services",
    response_model=List[ServiceOut],
    summary="List provider's owned services",
    description="Retrieves all services (active & inactive) created by the authenticated provider."
)
async def list_my_services(
    current_user: User = Depends(get_current_provider),
    db: AsyncSession = Depends(get_db)
) -> List[ServiceOut]:
    """List services owned by current provider.

    Args:
        current_user (User): Current provider user.
        db (AsyncSession): Database session.

    Returns:
        List[ServiceOut]: List of provider's services.
    """
    return await get_provider_services(db, current_user.id)


@router.get(
    "/{service_id}",
    response_model=ServiceOut,
    summary="Get service by ID",
    description="Retrieves details for a single service by ID."
)
async def get_service(
    service_id: int,
    db: AsyncSession = Depends(get_db)
) -> ServiceOut:
    """Get service detail.

    Args:
        service_id (int): Target service ID.
        db (AsyncSession): Database session.

    Returns:
        ServiceOut: Service payload.
    """
    return await get_service_by_id(db, service_id)


@router.post(
    "",
    response_model=ServiceOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Service (Provider only)",
    description="Creates a new service offered by the authenticated provider."
)
async def create_new_service(
    service_in: ServiceCreate,
    current_user: User = Depends(get_current_provider),
    db: AsyncSession = Depends(get_db)
) -> ServiceOut:
    """Create service endpoint.

    Args:
        service_in (ServiceCreate): Service data payload.
        current_user (User): Current provider user.
        db (AsyncSession): Database session.

    Returns:
        ServiceOut: Created service object.
    """
    return await create_service(db, current_user.id, service_in)


@router.put(
    "/{service_id}",
    response_model=ServiceOut,
    summary="Update a Service (Provider only)",
    description="Updates an existing service owned by the authenticated provider."
)
async def update_existing_service(
    service_id: int,
    service_in: ServiceUpdate,
    current_user: User = Depends(get_current_provider),
    db: AsyncSession = Depends(get_db)
) -> ServiceOut:
    """Update service endpoint.

    Args:
        service_id (int): Service ID to update.
        service_in (ServiceUpdate): Update values.
        current_user (User): Current provider user.
        db (AsyncSession): Database session.

    Returns:
        ServiceOut: Updated service record.
    """
    return await update_service(db, service_id, current_user.id, service_in)


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Service (Provider only)",
    description="Deletes a service owned by the authenticated provider."
)
async def delete_existing_service(
    service_id: int,
    current_user: User = Depends(get_current_provider),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete service endpoint.

    Args:
        service_id (int): Target service ID.
        current_user (User): Current provider user.
        db (AsyncSession): Database session.
    """
    await delete_service(db, service_id, current_user.id)
