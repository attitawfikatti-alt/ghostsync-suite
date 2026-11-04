import logging
import os
from .config import LOG_DIR

LOG_FILE = os.path.join(LOG_DIR, "ghostsync.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log_info(msg):
    logging.info(msg)
    print(f"\033[92m[✓]\033[0m {msg}")

def log_warn(msg):
    logging.warning(msg)
    print(f"\033[93m[!]\033[0m {msg}")

def log_error(msg):
    logging.error(msg)
    print(f"\033[91m[✗]\033[0m {msg}")
