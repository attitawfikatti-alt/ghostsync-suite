import os
import base64
import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from core.config import KEY_PATH
from core.logger import log_info, log_error

def derive_key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def export_encrypted_key(output_dir="/sdcard/Download"):
    if not os.path.exists(KEY_PATH):
        log_error(f"ملف المفتاح غير موجود: {KEY_PATH}")
        return False

    if not os.path.exists(output_dir):
        output_dir = os.path.expanduser("~")

    print("\n\033[93m[!] سيتم تشفير نسخة المفتاح بكلمة مرور مخصصة.\033[0m")
    pwd1 = getpass.getpass("أدخل كلمة مرور حماية المفتاح الاحتياطي: ").strip()
    pwd2 = getpass.getpass("أعد إدخال كلمة المرور: ").strip()

    if pwd1 != pwd2 or not pwd1:
        log_error("كلمتا المرور غير متطابقتين أو فارغتان.")
        return False

    try:
        with open(KEY_PATH, "rb") as f:
            raw_key = f.read()

        salt = os.urandom(16)
        derived = derive_key_from_password(pwd1, salt)
        fernet = Fernet(derived)
        encrypted_key_payload = fernet.encrypt(raw_key)

        dest_file = os.path.join(output_dir, "ghostsync_master_key.backup.enc")
        with open(dest_file, "wb") as f:
            f.write(salt + encrypted_key_payload)

        log_info(f"تم تصدير المفتاح مشفراً بنجاح إلى: {dest_file}")
        return True
    except Exception as e:
        log_error(f"فشل تصدير المفتاح: {e}")
        return False
