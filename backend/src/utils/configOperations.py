import json
import os
from typing import Optional

script_dir = os.path.dirname(__file__)
config_path = os.path.join(script_dir, "..", "..", "config", "config.json")

def load_config(config_key: Optional[str] = None) -> dict[str, any]:
    """
    Reads the config file and returns the specified key's value.

    :param config_key: The key to retrieve from the config file.
    :return: The value associated with the specified key.
    """
    with open(config_path, "r") as f:
        if config_key is None:
            return json.load(f)
        return json.load(f).get(config_key)

def set_config(config_key: str, value: any) -> None:
    """
    Sets the specified key in the config file to the provided value.

    :param config_key: The key to set in the config file.
    :param value: The value to set for the specified key.
    """
    config: dict[str, dict[str, any]] = load_config()
    config[config_key] = value

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)