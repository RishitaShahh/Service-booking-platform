"""User SQLAlchemy ORM model definition."""

from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class UserRole(str, PyEnum):
    """Enumeration of user roles within the platform."""
    CUSTOMER = "customer"
    PROVIDER = "provider"


class User(Base):
    """User ORM model representing platform users (Customers and Service Providers).

    Attributes:
        id (int): Primary key identifier.
        email (str): Unique email address used for login.
        hashed_password (str): Bcrypt hashed password.
        full_name (str): User's display full name.
        phone (Optional[str]): Contact phone number.
        role (UserRole): Role assigned ('customer' or 'provider').
        created_at (datetime): Account creation timestamp.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    role: Mapped[str] = mapped_column(
        String(50),
        default=UserRole.CUSTOMER.value,
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    services: Mapped[List["Service"]] = relationship(
        "Service", back_populates="provider", cascade="all, delete-orphan"
    )
    slots: Mapped[List["TimeSlot"]] = relationship(
        "TimeSlot", back_populates="provider", cascade="all, delete-orphan"
    )
    customer_bookings: Mapped[List["Booking"]] = relationship(
        "Booking",
        foreign_keys="Booking.customer_id",
        back_populates="customer",
        cascade="all, delete-orphan"
    )
    provider_bookings: Mapped[List["Booking"]] = relationship(
        "Booking",
        foreign_keys="Booking.provider_id",
        back_populates="provider",
        cascade="all, delete-orphan"
    )
