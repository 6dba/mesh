from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_key: str = "default-key"
    database_url: str = "sqlite+aiosqlite:///./kosatka.db"
    webhook_secret: str = "default-webhook-secret"
    sync_interval: int = 60
    expiration_check_interval: int = 300

    model_config = SettingsConfigDict(env_prefix="KOSATKA_", env_file=".env")


settings = Settings()
