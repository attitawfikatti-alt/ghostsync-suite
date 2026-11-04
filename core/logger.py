import os
import datetime
from core.config import LOG_FILE

MAX_LOG_SIZE = 1024 * 1024  # 1 MB

def rotate_logs_if_needed():
    if not os.path.exists(LOG_FILE):
        return
    try:
        if os.path.getsize(LOG_FILE) >= MAX_LOG_SIZE:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_log = f"{LOG_FILE}.{timestamp}.bak"
            os.rename(LOG_FILE, backup_log)
            
            # الاحتفاظ بآخر 3 نسخ احتياطية فقط
            log_dir = os.path.dirname(LOG_FILE)
            backups = sorted([f for f in os.listdir(log_dir) if f.startswith("ghostsync.log.") and f.endswith(".bak")])
            while len(backups) > 3:
                oldest = backups.pop(0)
                os.remove(os.path.join(log_dir, oldest))
    except Exception:
        pass

def write_log(level: str, message: str):
    rotate_logs_if_needed()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [{level.upper()}] {message}\n"
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted)
    except Exception:
        pass

def log_info(msg: str):
    print(f"\033[92m[✓]\033[0m {msg}")
    write_log("INFO", msg)

def log_warn(msg: str):
    print(f"\033[93m[!]\033[0m {msg}")
    write_log("WARN", msg)

def log_error(msg: str):
    print(f"\033[91m[✗]\033[0m {msg}")
    write_log("ERROR", msg)
