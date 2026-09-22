"""Pydantic schemas for Service entity requests and responses."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.user import UserOut


class ServiceCreate(BaseModel):
    """Schema for creating a new Service (providers only)."""
    name: str = Field(..., min_length=2, max_length=255, description="Name of the service")
    description: str = Field("", description="Detailed description of service")
    duration_minutes: int = Field(..., gt=0, description="Duration in minutes (must be > 0)")
    price: float = Field(..., ge=0.0, description="Service price (must be >= 0.0)")
    is_active: bool = Field(default=True, description="Service availability flag")


class ServiceUpdate(BaseModel):
    """Schema for updating an existing Service."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, ge=0.0)
    is_active: Optional[bool] = None


class ServiceOut(BaseModel):
    """Schema for Service response payload."""
    id: int
    provider_id: int
    name: str
    description: str
    duration_minutes: int
    price: float
    is_active: bool
    created_at: datetime
    provider: Optional[UserOut] = None

    model_config = ConfigDict(from_attributes=True)
