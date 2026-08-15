from services.booking import create_booking


def test_create_booking():
    result = create_booking("u1", "c1", "10:00")
    assert result["id"]
