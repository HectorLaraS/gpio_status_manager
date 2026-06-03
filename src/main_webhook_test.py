from src.services.webhook_engine import execute_alert_actions


def main() -> None:
    test_alert = {
        "id": None,
        "alert_number": "ALR-TEST",
        "status": "TEST",
        "priority": "P3",
        "title": "Test Alert Action",
        "description": "This is a webhook test.",
        "router_id": 0,
        "router_name": "TEST-ROUTER",
        "router_description": "Webhook Engine Test",
        "rule_name": "TEST",
        "opened_at": None,
        "closed_at": None,
        "last_detected_at": None,
        "occurrence_count": 1,
    }

    execute_alert_actions(
        event_type="TEST",
        alert=test_alert,
    )


if __name__ == "__main__":
    main()