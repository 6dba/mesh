import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

CONFIG_DIR = Path.home() / ".kosatka"
CONFIG_FILE = CONFIG_DIR / "config.json"


class Config(BaseModel):
    base_url: str = "http://localhost:8000"
    api_key: Optional[str] = None


def load_config() -> Config:
    if not CONFIG_FILE.exists():
        return Config()

    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return Config(**data)
    except Exception:
        return Config()


def save_config(config: Config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config.model_dump(), f, indent=2)
