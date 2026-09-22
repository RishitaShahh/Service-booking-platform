"""Routers package initialization."""

from app.routers.auth import router as auth_router
from app.routers.services import router as services_router
from app.routers.slots import router as slots_router
from app.routers.bookings import router as bookings_router
from app.routers.providers import router as providers_router

__all__ = [
    "auth_router",
    "services_router",
    "slots_router",
    "bookings_router",
    "providers_router",
]
