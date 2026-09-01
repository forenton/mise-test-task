from datetime import date, timedelta

from httpx import AsyncClient


def booking_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "name": "Анна Иванова",
        "phone": "+79991234567",
        "booking_date": (date.today() + timedelta(days=1)).isoformat(),
        "booking_time": "19:00:00",
        "guests": 4,
    }
    payload.update(overrides)
    return payload


async def test_create_booking(client: AsyncClient) -> None:
    response = await client.post("/bookings", json=booking_payload())

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["status"] == "active"
    assert data["name"] == "Анна Иванова"


async def test_list_bookings_with_date_filter(client: AsyncClient) -> None:
    target_date = (date.today() + timedelta(days=2)).isoformat()
    other_date = (date.today() + timedelta(days=3)).isoformat()

    await client.post("/bookings", json=booking_payload(booking_date=target_date))
    await client.post(
        "/bookings",
        json=booking_payload(
            phone="+79991234568",
            booking_date=other_date,
            booking_time="20:00:00",
        ),
    )

    response = await client.get("/bookings", params={"date": target_date})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["booking_date"] == target_date


async def test_get_booking_by_id(client: AsyncClient) -> None:
    created = await client.post("/bookings", json=booking_payload())
    booking_id = created.json()["id"]

    response = await client.get(f"/bookings/{booking_id}")

    assert response.status_code == 200
    assert response.json()["id"] == booking_id


async def test_cancel_booking(client: AsyncClient) -> None:
    created = await client.post("/bookings", json=booking_payload())
    booking_id = created.json()["id"]

    response = await client.delete(f"/bookings/{booking_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


async def test_missing_booking_returns_404(client: AsyncClient) -> None:
    response = await client.get("/bookings/404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Бронь не найдена"}


async def test_validation_error_returns_422(client: AsyncClient) -> None:
    response = await client.post("/bookings", json=booking_payload(phone="123"))

    assert response.status_code == 422


async def test_busy_slot_returns_409(client: AsyncClient) -> None:
    payload = booking_payload()

    first_response = await client.post("/bookings", json=payload)
    second_response = await client.post(
        "/bookings",
        json={**payload, "phone": "+79991234568"},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Дата и время бронирования уже занята",
    }


async def test_cancelled_slot_can_be_booked_again(client: AsyncClient) -> None:
    payload = booking_payload()
    created = await client.post("/bookings", json=payload)
    await client.delete(f"/bookings/{created.json()['id']}")

    response = await client.post(
        "/bookings",
        json={**payload, "phone": "+79991234568"},
    )

    assert response.status_code == 201
