from src.repositories.wan_repository import get_selected_wan_routers
from src.services.gpio_status_service import sync_gpio_status_for_router


def run_status_poll() -> dict:
    stats = {
        "routers_processed": 0,
        "routers_success": 0,
        "routers_failed": 0,
        "gpio_status": 0,
        "alerts_detected": 0,
    }

    print("=" * 80)
    print("STATUS POLL STARTED")
    print("=" * 80)

    routers = get_selected_wan_routers()

    print(f"Routers con WAN seleccionada: {len(routers)}")

    for router in routers:
        stats["routers_processed"] += 1

        router_db_id = router["router_id"]
        wan_ip = router["ipv4_address"]

        try:
            gpio_status_count = sync_gpio_status_for_router(
                router_db_id=router_db_id,
                wan_ip=wan_ip,
            )

            stats["gpio_status"] += gpio_status_count
            stats["routers_success"] += 1

            print(
                f"  STATUS OK | "
                f"router_id={router_db_id} | "
                f"name={router['name']} | "
                f"wan_ip={wan_ip} | "
                f"gpio_status={gpio_status_count}"
            )

        except Exception as error:
            stats["routers_failed"] += 1

            print(
                f"  STATUS ERROR | "
                f"router_id={router_db_id} | "
                f"name={router['name']} | "
                f"wan_ip={wan_ip} | "
                f"error={error}"
            )

            continue

    print("=" * 80)
    print("STATUS POLL FINISHED")
    print(
        f"routers={stats['routers_processed']} | "
        f"success={stats['routers_success']} | "
        f"failed={stats['routers_failed']} | "
        f"gpio_status={stats['gpio_status']}"
    )
    print("=" * 80)

    return stats