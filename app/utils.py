import json
import os
from datetime import datetime

LOG_FILE = "logs/data_ingestion.log"


def save_raw_json(data: dict, filename: str, folder: str = "data/raw"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def log_ingestion(context: dict):
    os.makedirs("logs", exist_ok=True)
    context["timestamp"] = datetime.now().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(context, ensure_ascii=False) + "\n")
