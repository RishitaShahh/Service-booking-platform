"""Pydantic schemas for TimeSlot entity requests and responses."""

from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.slot import SlotStatus
from app.schemas.service import ServiceOut
from app.schemas.user import UserOut


class SlotCreate(BaseModel):
    """Schema for creating a single time slot."""
    service_id: Optional[int] = Field(None, description="Optional service ID to link slot")
    start_time: datetime = Field(..., description="Start timestamp of time slot")
    end_time: datetime = Field(..., description="End timestamp of time slot")
    status: SlotStatus = Field(default=SlotStatus.AVAILABLE, description="Status of slot")


class SlotBatchCreate(BaseModel):
    """Schema for batch-generating recurring or multiple time slots for a day."""
    service_id: Optional[int] = Field(None, description="Optional service ID to link slots")
    target_date: date = Field(..., description="Target date for slots (YYYY-MM-DD)")
    start_hour: int = Field(..., ge=0, le=23, description="Starting hour (0-23)")
    end_hour: int = Field(..., ge=1, le=24, description="Ending hour (1-24)")
    slot_duration_minutes: int = Field(60, gt=0, description="Duration per slot in minutes")


class SlotOut(BaseModel):
    """Schema for TimeSlot response payload."""
    id: int
    provider_id: int
    service_id: Optional[int] = None
    start_time: datetime
    end_time: datetime
    status: SlotStatus
    created_at: datetime
    service: Optional[ServiceOut] = None
    provider: Optional[UserOut] = None

    model_config = ConfigDict(from_attributes=True)
