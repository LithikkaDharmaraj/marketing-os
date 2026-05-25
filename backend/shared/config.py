from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    secret_key: str = "dev-secret-key"
    allowed_origins: str = "http://localhost:3000"

    # Database
    database_url: str = "postgresql+asyncpg://marketing_os:marketing_os_pass@localhost:5432/marketing_os"
    database_url_sync: str = "postgresql://marketing_os:marketing_os_pass@localhost:5432/marketing_os"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""

    # Temporal
    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "default"

    # LLM
    groq_api_key: str = ""
    groq_model_large: str = "llama-3.3-70b-versatile"
    groq_model_fast: str = "llama-3.1-8b-instant"
    groq_max_tokens: int = 4096

    # Scraping
    apify_api_key: str = ""
    apify_base_url: str = "https://api.apify.com/v2"

    # Service ports
    intake_service_port: int = 8001
    scraper_service_port: int = 8002
    intelligence_service_port: int = 8003
    positioning_service_port: int = 8004
    icp_service_port: int = 8005
    embedding_service_port: int = 8006
    campaign_context_service_port: int = 8007
    orchestrator_port: int = 8008
    notification_service_port: int = 8009

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
