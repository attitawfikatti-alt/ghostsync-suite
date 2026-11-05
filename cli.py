        print("\n\033[94m-        elif choice == "7":
            verify_vault_integrity()
        elif choice == "8":
            get_vault_statistics()
        elif choice == "9":
            run_benchmark()
        elif choice == "10":
            get_active_connections()-- أدوات التحليل والصيانة ---\033[0m")
        print(" [7] فحص سلامة وتكامل الخزنة (Integrity Check)")
        print(" [8] تحليل إحصائيات التخزين (Storage Stats)")
        print(" [9] قياس سرعة المعالج والتشفير (Benchmark)")
        print(" [10] مراقبة الاتصالات النشطة (Live Connections)")
        print(" [0] خروج")#!/usr/bin/env python3
import os
import sys
from modules.net_audit import run_audit
from modules.vault import encrypt_path, decrypt_file, list_vault, secure_shred
from modules.ai_engine import analyze_audit_report
from modules.sync_engine import sync_vault_to_cloud
from modules.backup import export_encrypted_key, restore_encrypted_key
from modules.reporter import export_audit_html
from core.log_viewer import view_logs
from core.security_guard import enforce_permissions
from modules.integrity import verify_vault_integrity
from modules.sync_engine import check_cloud_connection
from modules.benchmark import run_benchmark
from modules.stats import get_vault_statistics
from modules.conn_monitor import get_active_connections
from core.auth import verify_pin, change_pin
from core.config import VAULT_DIR

BANNER = """\033[96m
   ____ _               _   ____                  
  / ___| |__   ___  ___| |_/ ___| _   _ _ __   ___ 
 | |  _| '_ \ / _ \/ __| __\___ \| | | | '_ \ / __|
 | |_| | | | | (_) \__ \ |_ ___) | |_| | | | | (__ 
  \____|_| |_|\___/|___/\__|____/ \__, |_| |_|\___|
                                  |___/            
       >> Modular Security & Vault Suite <<
\033[0m"""

def menu():
    last_audit_data = []
    while True:
        os.system("clear")
        print(BANNER)
        print("\033[93m[1]\033[0m تدقيق الشبكة المحلية والأجهزة المتصلة")
        print("\033[93m[2]\033[0m تشفير ملف أو مجلد وإيداعه في الخزنة")
        print("\033[93m[3]\033[0m استعراض محتويات الخزنة المشفرة")
        print("\033[93m[4]\033[0m فك تشفير ملف/مجلد من الخزنة")
        print("\033[93m[5]\033[0m تحليل أمني ذكي لتقرير الشبكة (AI Security Audit)")
        print("\033[93m[6]\033[0m مزامنة الخزنة المشفرة إلى السحابة (Rclone)")
        print("\033[93m[7]\033[0m تصدير نسخة احتياطية مشفرة لمفتاح الخزنة")
        print("\033[93m[8]\033[0m تغيير رمز الحماية (PIN)")
        print("\033[91m[0]\033[0m خروج")
        print("-" * 50)
        
        choice = input("\033[92mاختر عملية:\033[0m ").strip()
        
        if choice == "1":
            print("\n" + "=" * 40)
            last_audit_data = run_audit()
            input("\nاضغط Enter للمتابعة...")
        elif choice == "2":
            path = input("\nأدخل مسار الملف أو المجلد المراد تشفيره: ").strip()
            encrypt_path(path)
            input("\nاضغط Enter للمتابعة...")
        elif choice == "3":
            print("\n=== محتويات الخزنة ===")
            files = list_vault()
            if files:
                for idx, f in enumerate(files, 1):
                    print(f"[{idx}] {f}")
            else:
                print("الخزنة فارغة حالياً.")
            input("\nاضغط Enter للمتابعة...")
        elif choice == "4":
            files = list_vault()
            if not files:
                print("\nالخزنة فارغة.")
            else:
                print("\nالملفات المتوفرة:")
                for idx, f in enumerate(files, 1):
                    print(f"[{idx}] {f}")
                target = input("\nأدخل اسم الملف المشفر كاملاً (مع .enc): ").strip()
                full_path = os.path.join(VAULT_DIR, target)
                decrypt_file(full_path)
            input("\nاضغط Enter للمتابعة...")
        elif choice == "5":
            print("\n" + "=" * 40)
            if not last_audit_data:
                print("جاري فحص الشبكة أولاً للحصول على بيانات حديثة...")
                last_audit_data = run_audit()
            report = analyze_audit_report(last_audit_data)
            print("\n" + "-" * 20 + " تقرير التحليل الأمني " + "-" * 20)
            print(report)
            input("\nاضغط Enter للمتابعة...")
        elif choice == "6":
            print("\n" + "=" * 40)
            sync_vault_to_cloud()
            input("\nاضغط Enter للمتابعة...")
        elif choice == "7":
            export_encrypted_key()
            input("\nاضغط Enter للمتابعة...")
        elif choice == "8":
            change_pin()
            input("\nاضغط Enter للمتابعة...")
        elif choice == "0":
            print("\nإغلاق GhostSync... في أمان الله.")
            sys.exit(0)
        else:
            input("\nخيار غير صالح. اضغط Enter للمحاولة مجدداً...")

def handle_cli_args():
    if len(sys.argv) < 2:
        if not verify_pin():
            sys.exit(1)
        menu()
        return

    cmd = sys.argv[1].lower()
    if cmd in ["decrypt", "-d", "encrypt", "-e", "backup-key", "change-pin"]:
        if not verify_pin():
            sys.exit(1)

    if cmd in ["audit", "-a"]:
        data = run_audit()
        print(f"\n[✓] تم انتهاء التدقيق: تم اكتشاف {len(data)} جهاز.")
    elif cmd in ["scan-all", "--all"]:
        data = run_audit()
        report = analyze_audit_report(data, save_to_vault=True)
        print(report)
        sync_vault_to_cloud()
    elif cmd in ["encrypt", "-e"]:
        if len(sys.argv) < 3:
            print("الاستخدام: ghostsync encrypt <path>")
            sys.exit(1)
        encrypt_path(sys.argv[2])
        if len(sys.argv) > 3 and sys.argv[3] == "--shred":
            secure_shred(sys.argv[2])
    elif cmd in ["decrypt", "-d"]:
        if len(sys.argv) < 3:
            print("الاستخدام: ghostsync decrypt <filename.enc>")
            sys.exit(1)
        target = sys.argv[2]
        full_path = os.path.join(VAULT_DIR, target) if not os.path.exists(target) else target
        decrypt_file(full_path)
    elif cmd in ["sync", "-s"]:
        sync_vault_to_cloud()
    elif cmd in ["restore-key"]:
        if len(sys.argv) < 3:
            print("الاستخدام: ghostsync restore-key <path_to_backup.enc>")
            sys.exit(1)
        restore_encrypted_key(sys.argv[2])
    elif cmd in ["backup-key"]:
        export_encrypted_key()
    elif cmd in ["export-html", "--html"]:
        data = run_audit()
        report_text = analyze_audit_report(data, save_to_vault=False)
        export_audit_html(data, report_text)
    elif cmd in ["logs", "log"]:
        level = None
        if len(sys.argv) > 2:
            arg = sys.argv[2].lower()
            if "err" in arg:
                level = "error"
            elif "warn" in arg:
                level = "warn"
        view_logs(filter_level=level)
    elif cmd in ["check", "verify"]:
        verify_vault_integrity()
    elif cmd in ["check-cloud"]:
        check_cloud_connection()
    elif cmd in ["stats", "vault-stats", "disk"]:
        get_vault_statistics()
    elif cmd in ["benchmark", "bench", "speed"]:
        run_benchmark()
    elif cmd in ["update"]:
        print("033[96m[~] جاري التحقق من تحديثات المستودع...033[0m")
        os.system("cd ~/ghostsync && git pull origin main && chmod +x ~/ghostsync/cli.py")
    elif cmd in ["change-pin"]:
        change_pin()
    elif cmd in ["ai", "--ai"]:
        data = run_audit()
        print(analyze_audit_report(data))
    elif cmd in ["list", "-l"]:
        files = list_vault()
        for f in files:
            print(f)
    else:
        print(f"أمر غير معروف: {cmd}")
        print("الأوامر المتاحة: audit, scan-all, encrypt, decrypt, sync, backup-key, change-pin, ai, list")

if __name__ == "__main__":
    enforce_permissions()
    handle_cli_args()

def update_suite():
    print("\n\033[96m=== جلب التحديثات من GitHub (Auto-Update) ===\033[0m")
    import subprocess
    try:
        res = subprocess.run(["git", "pull", "origin", "main"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(res.stdout)
        if res.returncode == 0:
            print("\033[92m[✓] تم تحديث GhostSync إلى آخر إصدار بنجاح.\033[0m")
        else:
            print(f"\033[91m[!] تعذر التحديث: {res.stderr}\033[0m")
    except Exception as e:
        print(f"\033[91m[!] خطأ أثناء الاتصال: {e}\033[0m")
