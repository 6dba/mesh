from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_key: str = "change-me-agent"
    provider_type: str = "wireguard"  # Default provider
    
    # Provider specific settings
    marzban_url: str | None = None
    marzban_username: str | None = None
    marzban_password: str | None = None
    
    awg_config_path: str = "/etc/amnezia/amneziawg/wg0.conf"
    wg_config_path: str = "/etc/wireguard/wg0.conf"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
