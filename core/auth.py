import os
import hashlib
import getpass
from core.config import BASE_DIR
from core.logger import log_info, log_warn, log_error

PIN_FILE = os.path.join(BASE_DIR, ".ghostsync_pin")

def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode('utf-8')).hexdigest()

def is_pin_set() -> bool:
    return os.path.exists(PIN_FILE)

def setup_pin():
    print("\n\033[93m[!] إعداد رمز حماية جديد للمنظومة.\033[0m")
    while True:
        p1 = input("أدخل رمز PIN جديد (4 أرقام أو أكثر): ").strip()
        if len(p1) < 4:
            print("الرمز قصير جداً، يجب أن يتكون من 4 خانات على الأقل.")
            continue
        p2 = input("أعد إدخال رمز PIN للتأكيد: ").strip()
        if p1 != p2:
            print("الرمزان غير متطابقين، حاول مجدداً.")
            continue
        
        with open(PIN_FILE, "w") as f:
            f.write(hash_pin(p1))
        os.chmod(PIN_FILE, 0o600)
        log_info("تم حفظ رمز الحماية بنجاح.")
        return True

def verify_pin(max_attempts=3) -> bool:
    if not is_pin_set():
        return setup_pin()

    with open(PIN_FILE, "r") as f:
        stored_hash = f.read().strip()

    attempts = 0
    while attempts < max_attempts:
        entered = input("\033[96mأدخل رمز PIN للدخول: \033[0m").strip()
        if hash_pin(entered) == stored_hash:
            return True
        attempts += 1
        remaining = max_attempts - attempts
        if remaining > 0:
            print(f"\033[91mرمز غير صحيح! المحاولات المتبقية: {remaining}\033[0m")
        else:
            log_error("تم تجاوز عدد المحاولات المسموح بها.")
    return False

def change_pin():
    print("\n=== تغيير رمز الحماية (PIN) ===")
    if not verify_pin():
        log_error("فشل التحقق من الهوية. لا يمكن تغيير الرمز.")
        return False
    return setup_pin()
