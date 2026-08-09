"""Configuration management for Archon."""

import json
import os
from pathlib import Path
from typing import Any


def load_config(config_path: str | None = None) -> dict[str, Any]:
    config: dict[str, Any] = {
        "llm_provider": "openai",
        "llm_model": "gpt-4o",
        "temperature": 0.3,
        "max_tokens": 4096,
    }

    user_config_path = Path.home() / ".config" / "archon" / "config.json"
    if user_config_path.exists():
        with open(user_config_path) as f:
            config.update(json.load(f))

    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            config.update(json.load(f))

    env_key = os.environ.get("ARCHON_OPENAI_KEY") or os.environ.get("OPENAI_API_KEY")
    if env_key:
        config["openai_api_key"] = env_key

    return config
