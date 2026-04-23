from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_key: str = "change-me-agent"
    provider_type: str = "wireguard"  # awg | wireguard | marzban | xray

    # Provider specific settings
    marzban_url: str | None = None
    marzban_username: str | None = None
    marzban_password: str | None = None

    awg_config_path: str = "/etc/amnezia/amneziawg/wg0.conf"
    awg_interface: str = "wg0"
    awg_server_info_path: str = "/opt/kosatka/agent/awg_server.json"
    awg_state_path: str = "/opt/kosatka/agent/awg_peers.json"

    wg_config_path: str = "/etc/wireguard/wg0.conf"
    wg_interface: str = "wg0"
    wg_state_path: str = "/opt/kosatka/agent/wg_peers.json"

    # Pydantic-settings reads AGENT_*-prefixed env vars so agent.env can cleanly
    # coexist with other services on the same host.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="AGENT_",
        extra="ignore",
    )


settings = Settings()
