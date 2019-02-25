import json
import os

CONFIG_FILE = os.path.join(os.getcwd(), ".env.json")


def open_and_parse(fn: str) -> dict:
    if os.path.isfile(fn):
        with open(fn, "r") as f:
            try:
                return json.load(f)
            except:
                return None
    return None


def set_env_vars():
    data = open_and_parse(CONFIG_FILE)
    if data:
        for k, v in data.items():
            os.environ[k] = v
