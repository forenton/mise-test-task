import re
from datetime import date, time, timedelta

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.booking import BookingStatus

NAME_PATTERN = re.compile(r"^[A-Za-zА-Яа-яЁё -]+$")
PHONE_PATTERN = re.compile(r"^(?:\+7|8)\d{10}$")
STARTING_HOUR = 12
LAST_HOUR = 22
ALLOWED_HOURS = set(range(STARTING_HOUR, LAST_HOUR + 1))
MAX_DAYS_GAP = 90



class BookingCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=120,
        examples=["Анна Иванова"],
    )
    phone: str = Field(examples=["+79991234567"])
    booking_date: date = Field(examples=["2026-09-10"])
    booking_time: time = Field(examples=["19:00"])
    guests: int = Field(ge=1, le=12, examples=[4])

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = " ".join(value.strip().split())
        if len(normalized) < 2:
            raise ValueError("Имя должно содержать хотя бы 2 символа")
        if not NAME_PATTERN.fullmatch(normalized):
            raise ValueError("Имя должно состоять только из букв, пробелов и дефисов")
        return normalized

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if PHONE_PATTERN.fullmatch(value):
            return value
        raise ValueError("Введите корректный номер: +7XXXXXXXXXX или 8XXXXXXXXXX (10 цифр после кода)")

    @field_validator("booking_date")
    @classmethod
    def validate_booking_date(cls, value: date) -> date:
        today = date.today()
        max_date = today + timedelta(days=MAX_DAYS_GAP)
        if value < today:
            raise ValueError("Дата бронирования не может предшествовать текущей дате")
        if value > max_date:
            raise ValueError(f"Бронирование возможно на даты, не превышающие {MAX_DAYS_GAP} дней со дня текущего оформления")
        return value

    @field_validator("booking_time")
    @classmethod
    def validate_booking_time(cls, value: time) -> time:
        if value.minute == 0 and value.second == 0 and value.microsecond == 0:
            if value.hour in ALLOWED_HOURS:
                return value
        raise ValueError(f"Бронирование осуществляется строго по часам в промежутке от {STARTING_HOUR}:00 до {LAST_HOUR}:00")


class BookingOut(BookingCreate):
    id: int
    status: BookingStatus

    model_config = ConfigDict(from_attributes=True)
