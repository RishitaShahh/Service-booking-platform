"""Schemas package initialization."""

from app.schemas.auth import UserRegister, UserLogin, Token, TokenData
from app.schemas.user import UserOut, UserUpdate
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceOut
from app.schemas.slot import SlotCreate, SlotBatchCreate, SlotOut
from app.schemas.booking import BookingCreate, BookingStatusUpdate, BookingOut, ProviderDashboardSummary

__all__ = [
    "UserRegister",
    "UserLogin",
    "Token",
    "TokenData",
    "UserOut",
    "UserUpdate",
    "ServiceCreate",
    "ServiceUpdate",
    "ServiceOut",
    "SlotCreate",
    "SlotBatchCreate",
    "SlotOut",
    "BookingCreate",
    "BookingStatusUpdate",
    "BookingOut",
    "ProviderDashboardSummary",
]
