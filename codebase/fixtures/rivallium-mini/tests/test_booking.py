import unittest

from services.booking import create_booking


class BookingTests(unittest.TestCase):
    def test_create_booking(self) -> None:
        result = create_booking("u1", "c1", "10:00")
        self.assertTrue(result["id"])
