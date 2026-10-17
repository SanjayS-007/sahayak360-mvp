import os
import socket
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings
from sqlalchemy.engine.url import make_url


def _host_resolves(host: str, port: int = 5432) -> bool:
    try:
        socket.getaddrinfo(host, port)
        return True
    except OSError:
        return False


@lru_cache(maxsize=8)
def prepare_async_database(raw: str) -> tuple[str, tuple[tuple[str, object], ...]]:
    """Normalize Render/Heroku-style URLs for SQLAlchemy + asyncpg.

    Render injects ``postgres://...@dpg-xxxx-a/db``. That hostname only exists
    on Render's private DNS, and this API's Docker service cannot resolve it
    (login then fails with ``gaierror``). When the private host does not
    resolve, use the public hostname and require TLS.
    """
    url = raw.strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    scheme = url.split("://", 1)[0]
    if scheme == "postgresql":
        url = "postgresql+asyncpg://" + url[len("postgresql://") :]

    parsed = make_url(url)
    query = dict(parsed.query)
    sslmode = str(query.pop("sslmode", "") or "").lower()
    query.pop("channel_binding", None)
    ssl_query = str(query.pop("ssl", "") or "").lower()

    host = parsed.host or ""
    port = parsed.port or 5432
    if host.startswith("dpg-") and "." not in host and not _host_resolves(host, port):
        region = os.getenv("RENDER_POSTGRES_REGION", "singapore")
        host = f"{host}.{region}-postgres.render.com"

    use_ssl = host.endswith(".render.com") or sslmode in {
        "require",
        "verify-ca",
        "verify-full",
    } or ssl_query in {"1", "true", "require"}

    parsed = parsed.set(host=host, query=query)
    connect_args: tuple[tuple[str, object], ...] = (("ssl", True),) if use_ssl else ()
    return parsed.render_as_string(hide_password=False), connect_args


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://sahayak:sahayak_dev_2026@localhost:5432/sahayak360"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j_dev_2026"
    NEO4J_DATABASE: str = "neo4j"
    GEMINI_API_KEY: str = ""
    JWT_SECRET: str = "change_this_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def async_database_url(self) -> str:
        return prepare_async_database(self.DATABASE_URL)[0]

    @property
    def asyncpg_connect_args(self) -> dict:
        return dict(prepare_async_database(self.DATABASE_URL)[1])

    @property
    def cors_origins_list(self) -> List[str]:
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        # The live app is served from this host. Keep it allowed even if the
        # Render env still lists an older Vercel project name.
        required = "https://sahayak360-mvp.vercel.app"
        if required not in origins:
            origins.append(required)
        return origins

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
