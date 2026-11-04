import os
from core.config import BASE_DIR, KEY_PATH, VAULT_DIR
from core.logger import log_info, log_error

PIN_FILE = os.path.join(BASE_DIR, ".ghostsync_pin")

def enforce_permissions():
    """قفل أذونات الملفات الحساسة (0600 للملفات، 0700 للمجلدات)"""
    try:
        # قفل مجلد الخزنة
        if os.path.exists(VAULT_DIR):
            os.chmod(VAULT_DIR, 0o700)
            for root, dirs, files in os.walk(VAULT_DIR):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o700)
                for f in files:
                    os.chmod(os.path.join(root, f), 0o600)

        # قفل المفتاح السري
        if os.path.exists(KEY_PATH):
            os.chmod(KEY_PATH, 0o600)

        # قفل ملف الـ PIN
        if os.path.exists(PIN_FILE):
            os.chmod(PIN_FILE, 0o600)

        return True
    except Exception as e:
        log_error(f"فشل ضبط أذونات الحماية الصارمة: {e}")
        return False
