import datetime
from pathlib import Path
from typing import Dict, Any

from yaml import safe_load, dump


base_dir = Path(__file__).parent.parent
config_dir = base_dir / "config"


def load_config(config: str) -> Dict[str, Any]:

    if not (config_dir / config).is_file():
        raise ValueError(f"Config file {config} not found in {config_dir}")

    with open(config_dir / config, "r") as file:
        return safe_load(file)


def update_last_run() -> Dict[str, str]:
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(config_dir / "state.yaml", "w") as file:
        dump({"last_run": now}, file)
    return {"last_run": now}


def fetch_openrouter_api_key_and_model() -> (str, str):
    """
    Load the OpenRouter API key and model name from `config/secrets.yaml`.

    Returns:
        tuple: (API key, model name)
    """
    try:
        secrets = load_config("secrets.yaml")
        api_key = secrets.get("openrouter_api_key", "")
        model = secrets.get("openrouter_model", "gpt-4")  # Default model
        return api_key, model
    except Exception as e:
        raise Exception(f"Failed to load OpenRouter API key or model from secrets.yaml: {e}")


