from yaml import safe_load, dump
from pathlib import Path
from typing import Dict, Any
import datetime


base_dir = Path(__file__).parent.parent
config_dir = base_dir / "config"

def load_config(config: str) -> Dict[str, Any]:

    if not (config_dir / config).is_file():
        raise ValueError(f"Config file {config} not found in {config_dir}")

    with open(config_dir / config, "r") as file:
        return safe_load(file)


def update_last_run() -> Dict[str, str]:
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(config_dir / "state.yam", "w") as file:
        dump(file, now)
    return {"last_run": now}

