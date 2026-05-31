import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


def get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in ("true", "1", "yes", "y")


@dataclass(frozen=True)
class NetCloudConfig:
    base_url: str
    cp_api_id: str
    cp_api_key: str
    ecm_api_id: str
    ecm_api_key: str
    timeout_seconds: int


@dataclass(frozen=True)
class NcosConfig:
    username: str
    password: str
    verify_ssl: bool
    timeout_seconds: int


@dataclass(frozen=True)
class DatabaseConfig:
    server: str
    database: str
    user: str
    password: str
    driver: str
    trust_certificate: str


@dataclass(frozen=True)
class AppConfig:
    poll_interval_minutes: int
    secret_key: str
    log_level: str
    log_path: str


@dataclass(frozen=True)
class Settings:
    netcloud: NetCloudConfig
    ncos: NcosConfig
    database: DatabaseConfig
    app: AppConfig


def load_settings() -> Settings:
    return Settings(
        netcloud=NetCloudConfig(
            base_url=os.getenv("NETCLOUD_BASE_URL", "https://www.cradlepointecm.com"),
            cp_api_id=os.getenv("CP_API_ID", ""),
            cp_api_key=os.getenv("CP_API_KEY", ""),
            ecm_api_id=os.getenv("ECM_API_ID", ""),
            ecm_api_key=os.getenv("ECM_API_KEY", ""),
            timeout_seconds=int(os.getenv("NETCLOUD_TIMEOUT_SECONDS", "30")),
        ),
        ncos=NcosConfig(
            username=os.getenv("NCOS_USERNAME", ""),
            password=os.getenv("NCOS_PASSWORD", ""),
            verify_ssl=get_bool_env("NCOS_VERIFY_SSL", False),
            timeout_seconds=int(os.getenv("NCOS_TIMEOUT_SECONDS", "10")),
        ),
        database=DatabaseConfig(
            server=os.getenv("DB_SERVER", "localhost"),
            database=os.getenv("DB_DATABASE", "CradlepointGPIO"),
            user=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", ""),
            driver=os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
            trust_certificate=os.getenv("DB_TRUST_CERTIFICATE", "yes"),
        ),
        app=AppConfig(
            poll_interval_minutes=int(os.getenv("POLL_INTERVAL_MINUTES", "5")),
            secret_key=os.getenv("APP_SECRET_KEY", "change_me"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_path=os.getenv("LOG_PATH", "logs/app.log"),
        ),
    )