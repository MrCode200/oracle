import json
import os

# Ensure the path is relative to the current script's directory
script_dir = os.path.dirname(__file__)  # Directory where the current script is located
config_path = os.path.join(script_dir, "..", "..", "config", "config.json")

def load_config(config_key: str) -> dict:
    with open(config_path, "r") as f:
        return json.load(f).get(config_key)