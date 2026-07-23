import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "data"

# caso não exista
LOG_DIR.mkdir(exist_ok=True)

def setup_logging():
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger("world-cup-hub")

logger = setup_logging()