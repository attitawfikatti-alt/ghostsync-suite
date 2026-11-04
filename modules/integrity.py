import os
from core.config import VAULT_DIR
from core.logger import log_info, log_warn, log_error
from modules.vault import load_or_create_key, list_vault

def verify_vault_integrity():
    files = list_vault()
    if not files:
        log_info("الخزنة فارغة، لا توجد ملفات لفحص تكاملها.")
        return True

    fernet = load_or_create_key()
    total = len(files)
    valid_count = 0
    corrupted = []

    print(f"\n\033[96m=== جاري فحص سلامة وتكامل ملفات الخزنة ({total} ملف) ===\033[0m")

    for f in files:
        file_path = os.path.join(VAULT_DIR, f)
        try:
            with open(file_path, "rb") as enc_file:
                token = enc_file.read()
            # التحقق من صحة التوقيع المشفر وسلامة البيانات
            fernet.decrypt(token)
            valid_count += 1
            print(f"\033[92m[✓ سليم]\033[0m {f}")
        except Exception:
            corrupted.append(f)
            print(f"\033[91m[✗ تالف أو غير قابل للفك]\033[0m {f}")

    print("-" * 55)
    if corrupted:
        log_error(f"تحذير! تم رصد {len(corrupted)} ملف تالف أو مشفر بمفتاح آخر.")
        return False
    else:
        log_info(f"اكتمل الفحص: جميع الملفات ({valid_count}/{total}) سليمة ومتطابقة 100%.")
        return True
