from src.services.status_poll_service import run_status_poll


def main() -> None:
    stats = run_status_poll()

    print("STATUS POLL RESULT")
    print("=" * 80)
    print(stats)


if __name__ == "__main__":
    main()