from datetime import UTC, date, datetime, time
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BookingStatus(StrEnum):
    active = "active"
    cancelled = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    booking_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    booking_time: Mapped[time] = mapped_column(Time, nullable=False, index=True)
    guests: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, native_enum=False),
        default=BookingStatus.active,
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
