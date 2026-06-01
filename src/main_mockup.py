from src.config import load_settings
from src.clients.ncos_client import NcosClient


def main() -> None:
    settings = load_settings()

    test_wan_ip = "10.110.35.110"

    print("Cradlepoint GPIO Monitor - NCOS Mockup Test")
    print("=" * 60)
    print(f"Router WAN IP: {test_wan_ip}")
    print(f"NCOS user: {settings.ncos.username}")
    print(f"Verify SSL: {settings.ncos.verify_ssl}")
    print("=" * 60)

    client = NcosClient()

    try:
        gpio_status = client.get_gpio_status(test_wan_ip)

        print("GPIO STATUS:")
        print(gpio_status)

    except Exception as error:
        print("ERROR al consultar NCOS:")
        print(error)


if __name__ == "__main__":
    main()