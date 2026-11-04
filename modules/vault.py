import os
from cryptography.fernet import Fernet
from core.config import VAULT_DIR
from core.logger import log_info, log_error

KEY_FILE = os.path.expanduser("~/.ghostsync_key")

def get_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    os.chmod(KEY_FILE, 0o600)
    log_info("تم توليد مفتاح تشفير جديد وتأمينه في ~/.ghostsync_key")
    return key

def encrypt_file(file_path):
    if not os.path.exists(file_path):
        log_error(f"الملف غير موجود: {file_path}")
        return False
    try:
        key = get_or_create_key()
        fernet = Fernet(key)
        with open(file_path, "rb") as f:
            data = f.read()
        encrypted_data = fernet.encrypt(data)
        filename = os.path.basename(file_path) + ".enc"
        dest_path = os.path.join(VAULT_DIR, filename)
        with open(dest_path, "wb") as f:
            f.write(encrypted_data)
        log_info(f"تم تشفير الملف بنجاح: {dest_path}")
        return dest_path
    except Exception as e:
        log_error(f"فشل التشفير: {e}")
        return False

def decrypt_file(enc_path, output_path=None):
    if not os.path.exists(enc_path):
        log_error(f"الملف المشفر غير موجود: {enc_path}")
        return False
    try:
        key = get_or_create_key()
        fernet = Fernet(key)
        with open(enc_path, "rb") as f:
            enc_data = f.read()
        decrypted_data = fernet.decrypt(enc_data)
        if not output_path:
            output_path = enc_path[:-4] if enc_path.endswith(".enc") else enc_path + ".dec"
        with open(output_path, "wb") as f:
            f.write(decrypted_data)
        log_info(f"تم فك التشفير واستعادة الملف: {output_path}")
        return output_path
    except Exception as e:
        log_error(f"فشل فك التشفير: {e}")
        return False

def list_vault():
    try:
        return [f for f in os.listdir(VAULT_DIR) if f.endswith(".enc")]
    except Exception:
        return []
