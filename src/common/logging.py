import logging
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parents[2] / "logs" / "app.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_logger(name: str = "autoscanner") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger
