from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking, BookingStatus
from app.schemas.booking import BookingCreate


class BookingService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_booking(self, booking_data: BookingCreate) -> Booking:
        if await self._is_slot_taken(booking_data):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Дата и время бронирования уже занята",
            )

        booking = Booking(**booking_data.model_dump(), status=BookingStatus.active)
        self._session.add(booking)
        await self._session.commit()
        await self._session.refresh(booking)
        return booking

    async def list_bookings(
        self,
        booking_date: date | None,
        limit: int,
        offset: int,
    ) -> list[Booking]:
        statement: Select[tuple[Booking]] = select(Booking).order_by(
            Booking.booking_date,
            Booking.booking_time,
            Booking.id,
        )
        if booking_date is not None:
            statement = statement.where(Booking.booking_date == booking_date)

        result = await self._session.execute(statement.limit(limit).offset(offset))
        return list(result.scalars().all())

    async def get_booking(self, booking_id: int) -> Booking:
        booking = await self._session.get(Booking, booking_id)
        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Бронь не найдена",
            )
        return booking

    async def cancel_booking(self, booking_id: int) -> Booking:
        booking = await self.get_booking(booking_id)
        booking.status = BookingStatus.cancelled
        await self._session.commit()
        await self._session.refresh(booking)
        return booking

    async def _is_slot_taken(self, booking_data: BookingCreate) -> bool:
        statement = (
            select(Booking.id)
            .where(Booking.booking_date == booking_data.booking_date)
            .where(Booking.booking_time == booking_data.booking_time)
            .where(Booking.status == BookingStatus.active)
            .limit(1)
        )
        result = await self._session.execute(statement)
        return result.scalar_one_or_none() is not None
