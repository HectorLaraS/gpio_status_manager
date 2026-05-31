import requests

from src.config import load_settings


class NetCloudClient:
    def __init__(self) -> None:
        settings = load_settings()
        self.base_url = settings.netcloud.base_url.rstrip("/")
        self.timeout = settings.netcloud.timeout_seconds

        self.headers = {
            "X-CP-API-ID": settings.netcloud.cp_api_id,
            "X-CP-API-KEY": settings.netcloud.cp_api_key,
            "X-ECM-API-ID": settings.netcloud.ecm_api_id,
            "X-ECM-API-KEY": settings.netcloud.ecm_api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}{endpoint}"

        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"NetCloud GET failed: {url} | "
                f"Status: {response.status_code} | "
                f"Response: {response.text}"
            )

        return response.json()
    
    def get_wan_net_devices_by_router(self, router_id: int, limit: int = 100) -> list[dict]:
        data = self._get(
            "/api/v2/net_devices/",
            params={
                "router": router_id,
                "mode": "wan",
                "limit": limit,
            },
        )

        return data.get("data", [])

    def get_routers_by_group(self, group_id: int, limit: int = 500) -> list[dict]:
        data = self._get(
            "/api/v2/routers/",
            params={
                "group": group_id,
                "limit": limit,
            },
        )

        return data.get("data", [])