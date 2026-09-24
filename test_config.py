
import json
from pathlib import Path

config_path = Path("config/abc.json")

with config_path.open("r", encoding="utf-8") as file:
    config = json.load(file)

print("[*] Configuration loaded successfully")
print("[*] Configuration structure:", type(config).__name__)
print("[*] Number of entries:", len(config))
