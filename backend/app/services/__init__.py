"""Services package initialization."""

from app.services.auth_service import (
    register_user,
    authenticate_user,
    get_current_user,
    get_current_provider,
    get_current_customer,
)
from app.services.service_service import (
    create_service,
    get_all_services,
    get_service_by_id,
    get_provider_services,
    update_service,
    delete_service,
)
from app.services.slot_service import (
    create_slot,
    batch_create_slots,
    get_available_slots,
    get_provider_slots,
    delete_slot,
)
from app.services.booking_service import (
    create_booking,
    cancel_booking,
    get_customer_bookings,
    get_provider_bookings,
    update_booking_status,
    get_provider_dashboard_summary,
)

__all__ = [
    "register_user",
    "authenticate_user",
    "get_current_user",
    "get_current_provider",
    "get_current_customer",
    "create_service",
    "get_all_services",
    "get_service_by_id",
    "get_provider_services",
    "update_service",
    "delete_service",
    "create_slot",
    "batch_create_slots",
    "get_available_slots",
    "get_provider_slots",
    "delete_slot",
    "create_booking",
    "cancel_booking",
    "get_customer_bookings",
    "get_provider_bookings",
    "update_booking_status",
    "get_provider_dashboard_summary",
]
