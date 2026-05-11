from tomllib import load
from pathlib import Path

def get_database_path():
    config = toml_init()
    return Path(config["config"]["database_path"])

def toml_init():
    with open("pyproject.toml", "rb") as f:
        config = load(f)
    return config