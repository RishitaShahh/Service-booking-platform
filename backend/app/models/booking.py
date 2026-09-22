"""Booking SQLAlchemy ORM model definition."""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.service import Service
    from app.models.slot import TimeSlot


class BookingStatus(str, PyEnum):
    """Enumeration of booking appointment states."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Booking(Base):
    """Booking ORM model representing customer reservations.

    Attributes:
        id (int): Primary key identifier.
        customer_id (int): Foreign key referencing User.id (customer).
        service_id (int): Foreign key referencing Service.id.
        provider_id (int): Foreign key referencing User.id (provider).
        slot_id (int): Foreign key referencing TimeSlot.id.
        status (BookingStatus): Explicit status ('pending', 'confirmed', 'cancelled', 'completed').
        notes (Optional[str]): Additional instructions or customer notes.
        booking_timestamp (datetime): Timestamp when reservation was created.
        created_at (datetime): Timestamp when database row was inserted.
    """

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    slot_id: Mapped[int] = mapped_column(
        ForeignKey("time_slots.id", ondelete="CASCADE"), nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(
        String(50), default=BookingStatus.CONFIRMED.value, nullable=False, index=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    booking_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    customer: Mapped["User"] = relationship(
        "User", foreign_keys=[customer_id], back_populates="customer_bookings"
    )
    provider: Mapped["User"] = relationship(
        "User", foreign_keys=[provider_id], back_populates="provider_bookings"
    )
    service: Mapped["Service"] = relationship("Service", back_populates="bookings")
    slot: Mapped["TimeSlot"] = relationship("TimeSlot", back_populates="booking")
