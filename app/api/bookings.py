from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.booking import BookingCreate, BookingOut
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["bookings"])


def get_booking_service(
    session: AsyncSession = Depends(get_session),
) -> BookingService:
    return BookingService(session)


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: BookingCreate,
    service: BookingService = Depends(get_booking_service),
) -> BookingOut:
    return await service.create_booking(booking)


@router.get("", response_model=list[BookingOut])
async def list_bookings(
    booking_date: date | None = Query(default=None, alias="date"),
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: BookingService = Depends(get_booking_service),
) -> list[BookingOut]:
    return await service.list_bookings(
        booking_date=booking_date,
        limit=limit,
        offset=offset,
    )


@router.get("/{booking_id}", response_model=BookingOut)
async def get_booking(
    booking_id: int,
    service: BookingService = Depends(get_booking_service),
) -> BookingOut:
    return await service.get_booking(booking_id)


@router.delete("/{booking_id}", response_model=BookingOut)
async def cancel_booking(
    booking_id: int,
    service: BookingService = Depends(get_booking_service),
) -> BookingOut:
    return await service.cancel_booking(booking_id)
