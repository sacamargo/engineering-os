from api.controllers import post_booking


def main() -> None:
    print(post_booking({"user_id": "u1", "court_id": "c1", "slot": "10:00"}))


if __name__ == "__main__":
    main()
