# src/main_history_test.py

from src.repositories.gpio_status_repository import insert_gpio_status_history

insert_gpio_status_history(
    router_db_id=1,
    gpio_definition_id=1,
    status_key="TEST_KEY",
    raw_value=1,
    human_status="TEST_STATUS",
    is_alert=True,
)

print("History insert test completed")