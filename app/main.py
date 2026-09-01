from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.bookings import router as bookings_router
from app.core.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    await create_db_and_tables()
    yield


app = FastAPI(
    title="MISE Booking API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(bookings_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
