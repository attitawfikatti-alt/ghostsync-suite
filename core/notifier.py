import shutil
import subprocess
from core.logger import log_info

def send_alert(title: str, content: str, priority="high"):
    if not shutil.which("termux-notification"):
        return False
    try:
        cmd = [
            "termux-notification",
            "--title", f"🛡️ GhostSync: {title}",
            "--content", content,
            "--priority", priority,
            "--vibrate", "500,250,500"
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False
