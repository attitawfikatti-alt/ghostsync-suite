import os
import shutil
from core.config import VAULT_DIR, BASE_DIR
from core.logger import log_info

def format_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def get_vault_statistics():
    print("\n\033[96m=== إحصائيات الخزنة والتخزين (GhostSync Storage Analytics) ===\033[0m")
    
    if not os.path.exists(VAULT_DIR):
        print("مجلد الخزنة غير موجود.")
        return

    files = [f for f in os.listdir(VAULT_DIR) if f.endswith(".enc")]
    total_files = len(files)
    total_vault_size = 0
    file_details = []

    for f in files:
        f_path = os.path.join(VAULT_DIR, f)
        f_size = os.path.getsize(f_path)
        total_vault_size += f_size
        file_details.append((f, f_size))

    # ترتيب الملفات من الأكبر إلى الأصغر
    file_details.sort(key=lambda x: x[1], reverse=True)

    # حساب مساحة التخزين المتاحة على الجهاز
    disk_usage = shutil.disk_usage(BASE_DIR)
    free_space = disk_usage.free
    total_disk = disk_usage.total

    print(f"{'إجمالي الملفات المشفرة:':<28} \033[92m{total_files} ملف\033[0m")
    print(f"{'الحجم الإجمالي للخزنة:':<28} \033[93m{format_size(total_vault_size)}\033[0m")
    print(f"{'المساحة الحرة على القرص:':<28} \033[94m{format_size(free_space)} (من إجمالي {format_size(total_disk)})\033[0m")
    print("-" * 65)

    if file_details:
        print("\033[95mأكبر 5 ملفات مشفرة في الخزنة:\033[0m")
        print(f"{'اسم الملف':<45} | {'الحجم'}")
        print("-" * 65)
        for name, size in file_details[:5]:
            # اختصار الاسم إذا كان طويلاً
            display_name = (name[:42] + '...') if len(name) > 45 else name
            print(f"{display_name:<45} | {format_size(size)}")
    else:
        print("الخزنة فارغة حالياً.")
    print("=" * 65)
    log_info("اكتمل استعراض إحصائيات التخزين.")
