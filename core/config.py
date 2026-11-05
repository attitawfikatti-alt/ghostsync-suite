import os

BASE_DIR = os.path.expanduser("~/ghostsync")
VAULT_DIR = os.path.join(BASE_DIR, "storage", "vault")
LOG_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

KEY_PATH = os.path.join(BASE_DIR, ".vault_key")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

LOG_FILE = os.path.join(LOG_DIR, "ghostsync.log")

DEFAULT_SUBNET = "192.168.8.0/24"
CRITICAL_PORTS = [22, 8022, 5555, 80, 443, 8080]
SCAN_TIMEOUT = 1.0

os.makedirs(VAULT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
