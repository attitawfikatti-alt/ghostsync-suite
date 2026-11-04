import os
import tarfile
import shutil
from cryptography.fernet import Fernet
from core.config import KEY_PATH, VAULT_DIR
from core.logger import log_info, log_warn, log_error

def load_or_create_key():
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
        os.chmod(KEY_PATH, 0o600)
        log_info("تم إنشاء مفتاح تشفير جديد.")
    else:
        with open(KEY_PATH, "rb") as f:
            key = f.read()
    return Fernet(key)

def encrypt_path(target_path):
    target_path = os.path.expanduser(target_path).rstrip("/")
    if not os.path.exists(target_path):
        log_error(f"المسار غير موجود: {target_path}")
        return False

    fernet = load_or_create_key()
    base_name = os.path.basename(target_path)
    is_dir = os.path.isdir(target_path)

    try:
        if is_dir:
            archive_path = f"{target_path}.tar.gz"
            log_info(f"جاري أرشفة المجلد: {base_name}...")
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(target_path, arcname=base_name)
            read_path = archive_path
            dest_name = f"{base_name}.tar.gz.enc"
        else:
            read_path = target_path
            dest_name = f"{base_name}.enc"

        with open(read_path, "rb") as f:
            data = f.read()

        encrypted_data = fernet.encrypt(data)
        dest_path = os.path.join(VAULT_DIR, dest_name)

        with open(dest_path, "wb") as f:
            f.write(encrypted_data)

        if is_dir and os.path.exists(archive_path):
            os.remove(archive_path)

        log_info(f"تم التشفير بنجاح: {dest_path}")
        return True
    except Exception as e:
        log_error(f"فشل التشفير: {e}")
        return False

def decrypt_file(enc_path):
    enc_path = os.path.expanduser(enc_path)
    if not os.path.exists(enc_path):
        log_error(f"الملف المشفر غير موجود: {enc_path}")
        return False

    fernet = load_or_create_key()
    try:
        with open(enc_path, "rb") as f:
            encrypted_data = f.read()

        decrypted_data = fernet.decrypt(encrypted_data)
        base_name = os.path.basename(enc_path)

        if base_name.endswith(".tar.gz.enc"):
            original_archive = base_name.replace(".enc", "")
            out_archive_path = os.path.join(VAULT_DIR, original_archive)
            with open(out_archive_path, "wb") as f:
                f.write(decrypted_data)
            
            log_info(f"جاري استخراج المجلد من الأرشيف: {original_archive}...")
            with tarfile.open(out_archive_path, "r:gz") as tar:
                tar.extractall(path=VAULT_DIR)
            os.remove(out_archive_path)
            log_info(f"تم استرجاع المجلد بنجاح في: {VAULT_DIR}")
        elif base_name.endswith(".enc"):
            original_name = base_name[:-4]
            out_path = os.path.join(VAULT_DIR, original_name)
            with open(out_path, "wb") as f:
                f.write(decrypted_data)
            log_info(f"تم فك التشفير بنجاح: {out_path}")
        return True
    except Exception as e:
        log_error(f"فشل فك التشفير: {e}")
        return False

def list_vault():
    if not os.path.exists(VAULT_DIR):
        return []
    return [f for f in os.listdir(VAULT_DIR) if f.endswith(".enc")]
