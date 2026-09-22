"""Pydantic schemas for User entity representations."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from app.models.user import UserRole


class UserOut(BaseModel):
    """Schema for public/authenticated User response payload."""
    id: int
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Schema for updating User profile."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
