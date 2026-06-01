import urllib3
import requests

from src.config import load_settings


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NcosClient:
    def __init__(self) -> None:
        settings = load_settings()

        self.username = settings.ncos.username
        self.password = settings.ncos.password
        self.verify_ssl = settings.ncos.verify_ssl
        self.timeout = settings.ncos.timeout_seconds

    def get_status(self, wan_ip: str) -> dict:
        url = f"https://{wan_ip}/api/status"

        try:
            response = requests.get(
                url,
                auth=(self.username, self.password),
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout as error:
            raise RuntimeError(f"NCOS timeout: {url}") from error
        except requests.exceptions.RequestException as error:
            raise RuntimeError(f"NCOS request error: {url} | {error}") from error

        if response.status_code != 200:
            response_preview = response.text[:500]

            raise RuntimeError(
                f"NCOS GET failed: {url} | "
                f"Status: {response.status_code} | "
                f"Response: {response_preview}"
            )

        return response.json()

    def get_gpio_status(self, wan_ip: str) -> dict:
        status_data = self.get_status(wan_ip)

        # Caso 1: /api/status responde {"success": true, "data": {"gpio": {...}}}
        gpio_status = (
            status_data
            .get("data", {})
            .get("gpio", {})
        )

        if gpio_status:
            return gpio_status

        # Caso 2: /api/status responde {"success": true, "data": {"status": {"gpio": {...}}}}
        gpio_status = (
            status_data
            .get("data", {})
            .get("status", {})
            .get("gpio", {})
        )

        return gpio_status