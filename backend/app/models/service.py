"""Service SQLAlchemy ORM model definition."""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Service(Base):
    """Service ORM model representing services offered by providers.

    Attributes:
        id (int): Primary key identifier.
        provider_id (int): Foreign key referencing User.id (provider).
        name (str): Title or name of the service.
        description (str): Detailed summary of what the service entails.
        duration_minutes (int): Duration of appointment in minutes.
        price (float): Cost of the service.
        is_active (bool): Flag indicating if service is currently offered.
        created_at (datetime): Timestamp when service record was created.
    """

    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    provider: Mapped["User"] = relationship("User", back_populates="services")
    slots: Mapped[List["TimeSlot"]] = relationship(
        "TimeSlot", back_populates="service", cascade="all, delete-orphan"
    )
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking", back_populates="service", cascade="all, delete-orphan"
    )
