from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "NammaOpen"
    environment: str = "local"
    api_prefix: str = "/v1"
    app_domain: str = "http://localhost:8000"
    launch_city: str = "Bengaluru"
    default_language: str = "en"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "nammaopen"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    database_url: str | None = None
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/1"
    jwt_secret: str = "changeme"
    google_places_api_key: str | None = None
    basic_plan_price_inr: int = 99


@lru_cache
def get_settings() -> Settings:
    return Settings()
