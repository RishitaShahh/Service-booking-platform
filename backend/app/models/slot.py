"""TimeSlot SQLAlchemy ORM model definition."""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.service import Service
    from app.models.booking import Booking


class SlotStatus(str, PyEnum):
    """Enumeration of time slot states."""
    AVAILABLE = "available"
    BOOKED = "booked"
    BLOCKED = "blocked"


class TimeSlot(Base):
    """TimeSlot ORM model representing available appointment times.

    Attributes:
        id (int): Primary key identifier.
        provider_id (int): Foreign key referencing User.id (provider).
        service_id (Optional[int]): Foreign key referencing Service.id (optional).
        start_time (datetime): Appointment window start time.
        end_time (datetime): Appointment window end time.
        status (SlotStatus): Availability state ('available', 'booked', 'blocked').
        created_at (datetime): Timestamp when slot record was created.
    """

    __tablename__ = "time_slots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    service_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), nullable=True, index=True
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), default=SlotStatus.AVAILABLE.value, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    provider: Mapped["User"] = relationship("User", back_populates="slots")
    service: Mapped[Optional["Service"]] = relationship("Service", back_populates="slots")
    booking: Mapped[Optional["Booking"]] = relationship("Booking", back_populates="slot", uselist=False)
