from config import toml_init, get_database_path
from src.backend.app import get_app
import pandas as pd

config = toml_init()

try:
    dataset_path = config["config"]["dataset_path"]
except KeyError:
    print("No config->dataset_path found in pyproject.toml")
    exit(1)

app = get_app(dataset_path)
