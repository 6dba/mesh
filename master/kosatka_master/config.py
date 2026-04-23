from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Keys are deliberately separate:
    #   api_key       — clients calling the master (SDK, CLI, bot).
    #   agent_api_key — master calling the agent. Must match the value the
    #                   agent reads from AGENT_API_KEY.
    # Defaulting agent_api_key to api_key keeps single-host dev setups
    # working without needing to set both env vars.
    api_key: str = "default-key"
    agent_api_key: str = ""
    database_url: str = "sqlite+aiosqlite:///./kosatka.db"
    webhook_secret: str = "default-webhook-secret"
    sync_interval: int = 60
    expiration_check_interval: int = 300

    def effective_agent_api_key(self) -> str:
        return self.agent_api_key or self.api_key

    model_config = SettingsConfigDict(env_prefix="KOSATKA_", env_file=".env")


settings = Settings()
