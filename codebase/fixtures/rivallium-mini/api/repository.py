class BookingRepository:
    def save(self, payload: dict) -> dict:
        payload = dict(payload)
        payload["id"] = "b-1"
        return payload

    def delete(self, booking_id: str) -> bool:
        return bool(booking_id)
