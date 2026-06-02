from concurrent.futures import ThreadPoolExecutor, as_completed

from src.config import load_settings
from src.repositories.wan_repository import get_selected_wan_routers
from src.services.gpio_status_service import sync_gpio_status_for_router


def process_router_status(router: dict) -> dict:
    router_db_id = router["router_id"]
    wan_ip = router["ipv4_address"]

    try:
        gpio_status_count = sync_gpio_status_for_router(
            router_db_id=router_db_id,
            wan_ip=wan_ip,
        )

        return {
            "success": True,
            "router_id": router_db_id,
            "router_name": router["name"],
            "wan_ip": wan_ip,
            "gpio_status_count": gpio_status_count,
        }

    except Exception as error:
        return {
            "success": False,
            "router_id": router_db_id,
            "router_name": router["name"],
            "wan_ip": wan_ip,
            "error": str(error),
        }


def run_status_poll() -> dict:
    settings = load_settings()

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

    # TEMP TEST: descomenta esta línea para probar solo 25 routers primero
    routers = routers[:2]

    print(f"Routers con WAN seleccionada: {len(routers)}")
    print(f"Max workers: {settings.app.status_poll_max_workers}")

    with ThreadPoolExecutor(
        max_workers=settings.app.status_poll_max_workers
    ) as executor:
        futures = [
            executor.submit(process_router_status, router)
            for router in routers
        ]

        for future in as_completed(futures):
            result = future.result()

            stats["routers_processed"] += 1

            if result["success"]:
                stats["routers_success"] += 1
                stats["gpio_status"] += result["gpio_status_count"]

                print(
                    f"  STATUS OK | "
                    f"router_id={result['router_id']} | "
                    f"name={result['router_name']} | "
                    f"wan_ip={result['wan_ip']} | "
                    f"gpio_status={result['gpio_status_count']}"
                )

            else:
                stats["routers_failed"] += 1

                print(
                    f"  STATUS ERROR | "
                    f"router_id={result['router_id']} | "
                    f"name={result['router_name']} | "
                    f"wan_ip={result['wan_ip']} | "
                    f"error={result['error']}"
                )

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