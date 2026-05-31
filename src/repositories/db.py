import pyodbc
from src.config import load_settings


def build_connection_string() -> str:
    settings = load_settings()
    db = settings.database

    return (
        f"DRIVER={{{db.driver}}};"
        f"SERVER={db.server};"
        f"DATABASE={db.database};"
        f"UID={db.user};"
        f"PWD={db.password};"
        f"TrustServerCertificate={db.trust_certificate};"
    )


def get_connection():
    connection_string = build_connection_string()
    return pyodbc.connect(connection_string)