"""Pydantic schemas for Booking requests, responses, and provider analytics."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.booking import BookingStatus
from app.schemas.service import ServiceOut
from app.schemas.slot import SlotOut
from app.schemas.user import UserOut


class BookingCreate(BaseModel):
    """Schema for customer booking creation request payload."""
    service_id: int = Field(..., description="ID of service being booked")
    slot_id: int = Field(..., description="ID of time slot being booked")
    notes: Optional[str] = Field(None, description="Optional customer notes")


class BookingStatusUpdate(BaseModel):
    """Schema for provider update of booking status."""
    status: BookingStatus = Field(..., description="New booking status ('confirmed', 'cancelled', 'completed')")


class BookingOut(BaseModel):
    """Schema for Booking response payload."""
    id: int
    customer_id: int
    service_id: int
    provider_id: int
    slot_id: int
    status: BookingStatus
    notes: Optional[str] = None
    booking_timestamp: datetime
    created_at: datetime
    customer: Optional[UserOut] = None
    provider: Optional[UserOut] = None
    service: Optional[ServiceOut] = None
    slot: Optional[SlotOut] = None

    model_config = ConfigDict(from_attributes=True)


class ProviderDashboardSummary(BaseModel):
    """Schema for provider dashboard analytics summary."""
    total_services: int
    total_slots: int
    available_slots: int
    total_bookings: int
    upcoming_bookings_count: int
    completed_bookings_count: int
    total_revenue: float
    upcoming_bookings: List[BookingOut]
