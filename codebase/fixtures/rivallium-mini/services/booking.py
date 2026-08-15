"""Booking domain service."""

from api.repository import BookingRepository


def create_booking(user_id: str, court_id: str, slot: str) -> dict:
    repo = BookingRepository()
    return repo.save({"user_id": user_id, "court_id": court_id, "slot": slot})


def cancel_booking(booking_id: str) -> bool:
    repo = BookingRepository()
    return repo.delete(booking_id)
