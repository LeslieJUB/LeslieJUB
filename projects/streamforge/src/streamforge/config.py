from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "local"
    database_url: str = "postgresql+psycopg://streamforge:streamforge@localhost:5432/streamforge"
    kafka_bootstrap_servers: str = "localhost:29092"
    kafka_topic: str = "commerce.orders.v1"
    kafka_group_id: str = "streamforge-consumer"
    s3_endpoint_url: str | None = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_region: str = "eu-central-1"
    s3_bucket_bronze: str = "streamforge-bronze"
    s3_bucket_silver: str = "streamforge-silver"
    anomaly_amount_threshold: float = 5000
    anomaly_quantity_threshold: int = 100
    batch_size: int = 100
    batch_flush_seconds: int = 5
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
