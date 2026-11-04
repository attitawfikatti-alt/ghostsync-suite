import os
from core.config import LOG_FILE

def view_logs(filter_level=None, lines=30):
    if not os.path.exists(LOG_FILE):
        print("\033[93m[!] لا يوجد سجل أحداث حتى الآن.\033[0m")
        return

    print(f"\n\033[96m=== سجل العمليات والأحداث الأمنية (آخر {lines} سطر) ===\033[0m")
    if filter_level:
        print(f"\033[93mتصفية حسب المستوى: [{filter_level.upper()}]\033[0m")
    print("-" * 65)

    try:
        with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()

        matched = []
        for line in all_lines:
            if filter_level:
                if f"[{filter_level.upper()}]" in line:
                    matched.append(line)
            else:
                matched.append(line)

        display_lines = matched[-lines:]
        if not display_lines:
            print("لا توجد سجلات تطابق شرط التصفية.")
            return

        for line in display_lines:
            line_str = line.strip()
            if "[ERROR]" in line_str:
                print(f"\033[91m{line_str}\033[0m")
            elif "[WARN]" in line_str:
                print(f"\033[93m{line_str}\033[0m")
            elif "[INFO]" in line_str:
                print(f"\033[92m{line_str}\033[0m")
            else:
                print(line_str)
        print("-" * 65)
    except Exception as e:
        print(f"\033[91mخطأ أثناء قراءة السجل: {e}\033[0m")
