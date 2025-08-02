from yaml import safe_load
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


def update_last_run(dt: datetime):
    with open(config_dir / "last_run.txt", "w") as file:
        file.write(dt.strftime("%Y-%m-%d"))

