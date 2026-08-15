from services.booking import create_booking, cancel_booking


def post_booking(body: dict) -> dict:
    return create_booking(body["user_id"], body["court_id"], body["slot"])


def delete_booking(booking_id: str) -> dict:
    return {"ok": cancel_booking(booking_id)}
