import os

BASE_DIR = os.path.expanduser("~/ghostsync")
VAULT_DIR = os.path.join(BASE_DIR, "storage", "vault")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# تأمين وجود المجلدات المطلوبة
os.makedirs(VAULT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

DEFAULT_SUBNET = "192.168.1.0/24"
CRITICAL_PORTS = [22, 8022, 5555, 80, 443, 8080]
SCAN_TIMEOUT = 1.0
